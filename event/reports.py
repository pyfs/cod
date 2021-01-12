import logging
from collections import OrderedDict, Counter
from datetime import timedelta, datetime

from elasticsearch_dsl import Q
from elasticsearch_dsl import Search
from jinja2 import Template, Environment, PackageLoader

from account.models import User
from event.models import Event
from message.models import Message
from project.models import Project
from send_template.models import SendTemplate
from utils.elasticsearch import InitES
from django.db.models import Q
from utils.common.alert import EmailAlerter

logger = logging.getLogger('django')


class Reports(object):
    """ 报表模块的基础类"""

    def __init__(self, days=1):
        """ 初始化基础时间，过去一天24时间的范围
            this happened between 00:00:00 and 23:59:59 yesterday
        """
        # self.midnight = datetime.combine(timezone.now(), time.min)
        self.days = days
        self.midnight = datetime.now()
        self.yesterday_midnight = self.midnight - timedelta(days=self.days)

    def report(self, *args, **kwargs):
        pass


class OverViewStatistics(Reports):
    """ 概述过去24小时的内容"""

    def report(self) -> dict:
        # 事件数量
        events = Event.objects.filter(created__gte=self.yesterday_midnight, created__lte=self.midnight)
        # 消息数量
        messages = Message.objects.filter(created__gte=self.yesterday_midnight, created__lte=self.midnight)
        if events or messages:
            # 计算收敛比例
            converge_scale = '{:.2%}'.format(events.count() / messages.count())
        else:
            converge_scale = 0
        return dict(events=events.count(), messages=messages.count(), scale=converge_scale)


class ProjectTopStatistics(Reports):
    """ 统计过去24小时，以项目分类排行的项目列表"""

    def report(self, top=10) -> list:
        # 定义一个默认排序的字典
        all_projects_events = {}
        # 过滤有父层的项目，最后再次判断没有子层的项目
        # projects = list(filter(lambda x: x.get_children().last() is None, Project.objects.exclude(parent=None)))
        projects = list(filter(lambda x: x.get_children().last() is None, Project.objects.all()))
        for project in projects:
            # 查询项目关联事件数量
            events = Event.objects.filter(project=project).count()
            if events:
                all_projects_events[project] = events
        # 对字典的value(t[1]的关键指定, key排序则是t[0])进行倒序排序(reverse=True)
        order_events = OrderedDict(sorted(all_projects_events.items(), key=lambda t: t[1], reverse=True))
        return list(order_events.items())[:top - 1]


class ProjectRelationsStatistics(Reports):
    """ 项目的统计信息：事件、消息、收敛比例、事件类型的统计数 """

    def report(self, project: Project):
        """ 基于项目查询关联的统计数信息"""

        # 项目产生的事件
        events = Event.objects.filter(project=project).filter(created__gte=self.yesterday_midnight,
                                                              created__lte=self.midnight)
        # . 项目产生的消息
        messages = Message.objects.filter(project=project.name).filter(created__gte=self.yesterday_midnight,
                                                                       created__lte=self.midnight)
        # 4. 事件和消息收敛比例
        if messages:
            scale = '{:.2%}'.format(events.count() / messages.count())
        else:
            scale = 0
        # 5. 事件类型占比
        event_type_list = events.values_list("type", flat=True)  # 获取type字段内容为列表
        event_type_list_count = dict(Counter(event_type_list))
        # 生成统计数据
        statistics = dict(project=project, events=events, messages=messages, scale=scale,
                          type=event_type_list_count)
        return statistics


class ReportToEs(InitES):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push_data(self, data, es_index="cod-test-syslog"):
        if not self.check_data(data):
            logger.error("Check data is failed。")
            return False
        # 设置Document 属性
        for sub_data in data.items():
            k, v = sub_data
            setattr(self, k, v)
        # 保存数据到es里面
        result = ""
        try:
            result = self.save(index=es_index)
        except Exception as e:
            logger.error("Push data ES Failed, error:{}".format(e))
        if result == "created" or result == "updated":
            return True
        else:
            logger.error("Push data ES Failed")
            return False


class SearchToES(InitES):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def search_report(bz_index):
        s = Search(index=bz_index)
        midnight = datetime.now()
        yesterday_midnight = midnight - timedelta(days=1)
        s = s.filter("range", createtime={"gte": yesterday_midnight, "lt": midnight})
        q = Q("bool", must=[Q('match', type='report'), Q('match', env='uat'), Q("match", tags="report")])
        result = s.query(q).execute()
        return list(result)
        # for sub in result:
        #     print(sub.to_dict())


class ReportHandler(object):

    @staticmethod
    def template_to_content(content):
        """ 拿到报表汇总数据通过模板进行渲染出内容,每个模块都是单独渲染出数据返回，最后拼接根据顺序拼接在一起。
        content 样例数据, <Project: INFRA_CCLOUD> 这样格式的内容是给到返回对象，可进一步拓展查询。
        [{'over_view': (说明：字典内容)
            {'events': 4, 'messages': 5, 'scale': '80.00%'}
         },

         {'project_top': (说明: 列表嵌套的元组)
            (<Project: INFRA_CCLOUD>: 44,
            <Project: CSM_CSC>: 1)
         }]

         {'user_relations': (说明：列表嵌套的字典)
           [{'project': <Project: INFRA_CCLOUD>,
             'events': <QuerySet: events>,
             'messages': <QuerySet: messages>,
             'scale':  '80%'
             },
            {'project': <Project: INFRA_ITSM>,
             'events': <QuerySet: events>,
             'messages': <QuerySet: messages>,
             'scale':  '70%'
             'type': {'HostRestart': 1, 'ContainerHighCpu': 2, 'PowerSupplyCritical': 1, 'HostOutOfMemory': 7}
             },
           ]
        }

         参考的模板实例
         1. over_view 内容
         [COD] 24小时的概要数据
         总告警消息: {{ data['messages']}}
         发送告警事件: {{ data['events']}}
         消息：事件的收敛比例: {{ data['scale']}}

         2. project_top 内容
         项目事件排行榜
         {% for project in data %}
            项目：{{ project[0] }} 事件： {{ project[1] }}
         {% endfor %}

         3. user_relations 内容
         用户关联的项目信息
         {% for project in data  %}
        项目名称: {{ project['project'].name }}
        事件数量: {{ project['events'].count() }}
        消息数量: {{ project['messages'].count() }}
        收敛比例: {{ project['scale'] }}
        告警类型: {{ project['type'] }}
         {% endfor %}
        """
        # 告警平台数据
        # todo get模板的异常状态判断
        # todo debug修改数据，修改type=0 正常是2
        o_v_template = SendTemplate.objects.get(is_removed=False, type=2, name="report_over_view")
        o_v_content = Template(o_v_template.content).render(data=content['over_view'])
        # 项目TOP排行榜
        p_t_template = SendTemplate.objects.get(is_removed=False, type=2, name="report_project")
        p_t_content = Template(p_t_template.content).render(data=content['project_top'])
        p_t_content = p_t_content.replace('\n\n', '\n')
        # 用户关联项目的统计数据
        u_template = SendTemplate.objects.get(is_removed=False, type=2, name="report_user")
        u_content = Template(u_template.content).render(data=content['user_relations'])
        # 把所有内容拼接完成
        result = o_v_content + '\n\n' + p_t_content + '\n\n' + u_content
        return result

    @staticmethod
    def send_mail(user, title, content) -> bool:
        """ 发送内容给到目标用户"""

        try:
            EmailAlerter().alert(user, content, title=title)
        except Exception as error:
            logger.error(error)
            return False
        else:
            return True

    @staticmethod
    def send_report_mail_handler(report_type) -> None:
        """ 获取邮件报告内容
        # @param users: users对象
        @param report_type: 报告类型，daily,weekly,monthly
        """
        users = []
        users_obj = User.objects.filter(tags__isnull=False).distinct()

        # 查询到的用户列表为空直接返回空列表
        if users_obj is None:
            logger.debug('"{{Report action":"report target senders list is none"}}')
            return users_obj

        # 获取发送报告用户对象
        for user_obj in users_obj:
            if user_obj.get_user_tagtype(report_type):
                users.append(user_obj)
                logger.debug('"{{Report action":"report target senders list:{0}"}}'.format(user_obj.username))

        for user in users:
            # 获取用户标签和关联的项目
            tags = user.get_user_tags(report_type)
            if not tags:
                # 若报告类型的标签为空，跳出循环，不发送邮件
                logger.info('"{{Report action":"No tag with "user":"{0}"}}"'.format(user))
                continue
            over_view_statistics = OverViewStatistics().report()
            project_top_statistics = ProjectTopStatistics().report()
            projects = user.get_user_project()    # 获取用户关联的项目
            project_detail_content = []
            report_sender_list = []
            if projects:
                for project in projects:
                    for tag in tags:
                        key = '{report_type}_{tag}'.format(report_type=report_type, tag=tag)
                        project_detail_content.append(ReportHandler().get_project_content(project, key))
                        logger.info(
                            '"{{'
                            'Report action":"report receiver:{0} get "project_detail_content":{1}'
                            '}}"'.format(user, project_detail_content))

            title = '【COD告警平台】告警统计数据'
            report_sender_list.append(user.username)  # 邮件发送模块需要传递用户列表作为参数，格式转换
            logger.info('{{"Report action":"report receivers list":"{0}"}}'.format(report_sender_list))

            # 通过日报模板把内容渲染成html
            env = Environment(loader=PackageLoader('event', 'templates'))  # 配置环境路径
            report_template = env.get_template('template.html')  # 获取渲染模板
            # 渲染成html
            report_content = report_template.render(over_view_statistics=over_view_statistics.items(),
                                                    project_top_statistics=project_top_statistics,
                                                    project_detail_content=project_detail_content)

            # 发送日报
            send_result = ReportHandler().send_mail(report_sender_list, title,
                                                    content=u'{r_content}'.format(r_content=report_content))

            # 报告发送结果判断
            if send_result:
                logger.info('Report was sent successful')
            else:
                logger.error(
                    'Report was sent fail. "users": "{0}", "content": "{1}"'.format(report_sender_list, report_content))

    @staticmethod
    def get_project_content(project: Project, tags) -> None:
        """ 基于项目查询对应时间周期的统计数据，返回的是渲染完成的数据。只做项目相关统计查询，不做平台基础数据渲染

        Args:
            project:  项目对象入参
            tags:  查询字符串的方式，需要包括时间周期，参考内容 daily_project_relations
        """
        # 判断tags的入参结构
        period, tag = tags.split('_', 1)
        if period == 'daily':
            days = 1
        elif period == 'week':
            days = 7
        elif period == 'month':
            days = 30
        else:
            logger.error('Period time is error')
            return None
        # 获取对应时间周期的
        project_relations_content = ProjectRelationsStatistics(days=days).report(project)
        # 获取模板内容
        # todo debug修改数据，修改type = 0 正常是2
        p_r_template = SendTemplate.objects.get(is_removed=False, type=2, name=tag)
        p_r_content = Template(p_r_template.content).render(project=project_relations_content)
        return p_r_content

    @staticmethod
    def init_user_tags():
        """ 初始化用户标签"""
        # users = User.objects.filter(is_removed=False)
        users = User.objects.filter(username="zhengmingzai")
        tags_list = ["report:over_view", "report:project_top", "report:daily_project_relations"]
        for user in users:
            for tag in tags_list:
                user.tags.add(tag)

    def handler(self):
        """ 统一模块发送日志"""
        # 告警平台公共数据
        over_view_statistics = OverViewStatistics(days=2).report()
        project_top_statistics = ProjectTopStatistics(days=2).report()
        # 1. 查询所有用户
        for user in User.objects.filter(is_removed=False):
            # 用户关联的统计数据
            content = dict()
            # 判断用户的关联标签
            user_tags_all = [t.name for t in user.tags.all()]
            if not user_tags_all:
                continue
            # 判断用户标签对应的内容
            for tags in user_tags_all:
                if tags == "report:over_view":
                    # 添加 平台基础数据 给用户
                    if over_view_statistics:
                        content['over_view'] = over_view_statistics
                elif tags == "report:project_top":
                    # 添加 项目排行榜数据 给用户
                    if project_top_statistics:
                        content['project_top'] = project_top_statistics
                elif tags == "report:user_relations":
                    # 添加 用户关联项目的数据
                    user_statistics = ProjectRelationsStatistics().report(user)
                    if user_statistics:
                        content['user_relations'] = user_statistics
            # 基于模板渲染发送邮件内容
            content_result = self.template_to_content(content)
            # 发送邮件
            title = "【COD告警平台】告警统计数据"
            result = self.send_mail(user, title, content_result)
