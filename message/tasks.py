import logging
from datetime import timedelta

import requests
from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from jinja2 import Template
from model_utils.models import now

from converge.models import BurrConverge
from delivery.models import Delivery
from event.constants import STATUS_RESOLVED, STATUS_NOT_CLOSED, STATUS_TIMEOUT, STATUS_CLOSED
from event.models import Event
from event.reports import ReportHandler
from message.constants import STATUS_ALERT, STATUS_RECOVER, RULE_TYPES, LOOP_UPGRADE
from message.models import Message
from receive_strategy.constants import RECEIVE_CHOICES, TYPE_CHOICES, ALERT, RECOVERY
from receive_strategy.models import ReceiveStrategy
from send_template.models import SendTemplate
from utils.common.alert import ItapisWxAlerter, EmailAlerter, PhoneAlerter, SMSAlerter, WxAlerter
from utils.env import Env
from utils.ruleparser import RuleParser

logger = logging.getLogger('django')
env = Env()
HOOK_URL = env.get('HOOK_URL')
HOOK_TOKEN = env.get('HOOK_TOKEN')
HOOK_ON = env.get('HOOK_ON')


@shared_task(ignore_result=True)
def message_handler(message_id):
    """
    告警消息异步处理：告警收敛
    :param message_id: Message Object Id
    """
    message = Message.objects.get(id=message_id)  # 消息ID获取
    logger.info('{{"m_id":"{0}","action":"message come on","IP:"{1}"}}'.format(message.id, message.host))

    if message.status == STATUS_ALERT:
        # 告警消息生成事件
        handle_message_alert(message)
    elif message.status == STATUS_RECOVER:
        # 恢复消息关闭事件
        handle_message_recover(message)
    else:
        logger.warning('{{"m_id":"{0}","action":"Message status no support"}}'.format(message.id))
    # 是否调度到开发环境
    if HOOK_ON == 'true':
        post_message(message)


# 推送消息到本地开发环境进行调整
def post_message(message):
    play_data = {
        "project": message.project,
        "type": message.type,
        "host": message.host,
        "title": message.title,
        "level": str(message.level),
        "status": str(message.status),
    }
    headers = {"Authorization": "token %s" % HOOK_TOKEN}
    try:
        response = requests.post(url=HOOK_URL, headers=headers, data=play_data)
        logging.info('Post Hook COD, status %s, Hook cod %s, Hook on %s' % (response.status_code, HOOK_URL, HOOK_ON))
    except requests.exceptions.ConnectionError:
        logging.error('push message hook server connection error')


def handle_message_alert(message: Message) -> None:
    """
    处理异常告警消息
    :type message: object
    :param message: 当前上报消息
    """
    # 获取收敛规则的开启状态，如有开启的话启用削峰处理
    converge_status = message.get_project().converge_status
    if converge_status:  # 如果启用收敛消息的策略处理，实现对消息削峰的处理效果
        for converge in message.get_burr_converges():
            create_event(message, converge)
    else:
        # 找到消息同类的事件
        last_event = message.last_event()
        if last_event:
            # 合并已知事件
            last_event.messages.add(message)
            # 判断告警消息等级，如果高于当前事件则更新状态
            if last_event.level > message.level:
                last_event.leve = message.level
                last_event.save()
            logger.info('{{"m_id":"{0}","e_id":"{1}","action":"message merge to event {2}" }}'.format(message.id,
                                                                                                      last_event.id,
                                                                                                      last_event.name))
        else:
            # !!!![开始] 单独处理告警源的收敛情况，应对大量的告警进来!!!!!
            if message.data_source == 'ccloud':
                converge = BurrConverge.objects.get(name='ccloud')
                event = create_event(message, need_converge=converge)
            # !!!![结束] 单独处理告警源的收敛情况，应对大量的告警进来!!!!!
            else:
                # 创建新事件
                event = create_event(message)
            # 判断事件是否创建成功再进行下一步的通知调度
            if event:
                # 没有找到同类事件触发一个异步任务,处理整个发送环节的任务
                notification_processor(event.id)
                # 查找同类事件
                # if event.get_similar():
                #     logger.info('Find similar event to cancel the notification. ')
                # else:
                #     # 没有找到同类事件触发一个异步任务,处理整个发送环节的任务
                #     notification_processor(event.id)


@shared_task(ignore_result=True)
def notification_processor(event_id):
    """
    异步任务的方式处理整个消息发送的逻辑，涉及如下环节
    递归处理分派策略
    基于 event delivery 触发通知发送
    """
    # 基于事件ID拿到对象
    event = Event.objects.get(id=event_id)
    # 检查事件是否关闭状态
    if event.status in STATUS_CLOSED:
        logger.info('{{"e_id":"{0}","action":"event is closed, cancel notification processor."}}'.format(event_id))
        return None
    logger.debug('{{"e_id":"{0}","action":"event notification processor"}}'.format(event_id))
    # 获取当前分派策略
    delivery = event.current_delivery
    # 判断项目过滤规则，为空则执行后续的通知处理
    if event.project.filter_types:
        for rule_type in RULE_TYPES:
            event_type = '{type_format}.{rule_type}'.format(type_format=rule_type,
                                                            rule_type=getattr(event, rule_type))
            # 实例化并检查配置的规则类型是否为json格式
            ruleparser = RuleParser(event.project.filter_types, event_type)
            # 匹配黑名单规则
            rule_processor_result = ruleparser.processor('exclude')
            # 若规则匹配成功，从发送列表中剔除用户
            if rule_processor_result:
                logger.info(
                    '{{"e_id":"{0}","action":"Black list filter rules were matched successfully, user {1} removed '
                    'from the sender list"}}'.format(event.id, delivery.get_users()))
                return None

    # 判断分配策略为空则结束后续的通知处理
    if delivery:
        # 查询分派策略下group所有用户
        users_obj = delivery.get_users()
    else:
        logger.debug('{{"e_id":"{0}","action":"Delivery is None, cancel upgrade."}}'.format(event.id))
        return None

    # 遍历所有关联用户的阻断设置，找到目标用户
    target_users_obj = get_target_user(users_obj, event)
    # 获取发送的目标用户，用于debug使用
    target_users_list = [user.username for user in target_users_obj]
    if target_users_obj:
        # 遍历所有目标用户的接收策略，把目标用户分配到不同的发送渠道
        send_channel = get_send_channel(target_users_obj)
        logger.debug('{{"e_id":"{0}","action":"send channel list:{1}"}}'.format(event.id, send_channel))
        # 发送通知给用户
        msg_type = ALERT
        send_notification(send_channel, event, msg_type)
        logger.debug('{{"e_id":"{0}","action":"target users list:{1}"}}'.format(event.id, target_users_list))
    else:
        logger.warning('{{"e_id":"{0}","action":"target user list is None"}}'.format(event.id))

    # 最后处理完成通知的所有环节，对事件进行关联上一层分配策略
    upgrade_delivery = delivery.get_children().last()
    if upgrade_delivery and upgrade_delivery.get_upgrade_level(event.level):
        event.current_delivery = upgrade_delivery
        event.save()
        # 递归调用自身函数来处理通知
        logger.info('{{"e_id":"{0}","action":"event upgrade, send user list{1}"}}'.format(event.id, target_users_list))
        notification_processor.apply_async(args=[event.id], countdown=delivery.delay * 60)
    else:
        logger.info('{{"e_id":"{0}","action":"The event complete upgrade is over"}}'.format(event.id))

    # 用于递归调度给到项目管理员循环通知需要升级的告警
    if event.level in LOOP_UPGRADE:
        logger.info('{{"e_id":"{0}","action":"The event is of disaster level and is repeatedly sent to the '
                    'administrator."}}'.format(event.id))
        # 基于项目设置的发送频率
        notification_processor.apply_async(args=[event.id], countdown=event.project.upgrade_frequency)


def get_target_user(users_obj, event) -> list:
    """ 基于时间找到所有的用户列表，然后遍历如下功能列表对应的开关：
       1.是否开启全局打搅
       2.是否开启同类告警阻断策略
       3.用户沉默规则
       4.是否开启非工作时间的免打搅
       5.自定义免打搅时间
       6.回写事件关联的通知组进行关联
    """
    # 定义一个目标用户空列表
    target_users_obj = []
    # 传入用户列表为空直接返回空列表
    if users_obj is None:
        logger.debug('{{"action":"users object list is none"}}')
        return target_users_obj
    for user in users_obj:
        # 判断各类阻断规则，若符合，则剔除用户
        if user.global_immunity:  # 判断用户是否开启通知的【全局免扰】配置
            logger.info('{{"u_id":"{0}","action":"Global_immunity rule is enable, user {1} removed from the sender '
                        'list"}}'.format(user.id, user.username))
            continue
        elif user.similar_block:  # 判断用户是否开启事件处理的【同类阻断】配置
            logger.info('{{"u_id":"{0}","action":"Similar_block rule is enable,user {1} removed from the sender '
                        'list"}}'.format(user.id, user.username))
            continue
        elif user.get_silence_ignore_type():  # 判断用户是否启用沉默规则的【忽略类型】配置
            logger.info('{{"u_id":"{0}","action":"Silence rule is enable, user {1} removed from the sender list"}}'''
                        .format(user.id, user.username))
            continue
        elif user.filter_types:  # 用户规则类型过滤
            # 从事件名称中提取规则类型
            for rule_type in RULE_TYPES:
                event_type = '{type_format}.{rule_type}'.format(type_format=rule_type,
                                                                rule_type=getattr(event, rule_type))
                # 实例化并检查配置的规则类型是否为json格式
                ruleparser = RuleParser(user.filter_types, event_type)
                # 匹配黑名单规则
                rule_processor_result = ruleparser.processor('exclude')
                # 若规则匹配成功，从发送列表中剔除用户
                if rule_processor_result:
                    logger.info(
                        '{{"u_id":"{0}","action":"Black list filter rules were matched successfully, user {1} removed '
                        'from the sender list"}}'.format(user.id, user.username))
                    break
            else:
                target_users_obj.append(user)
                logger.debug('{{"u_id":{0},"action":"get_target_user() '
                             'user {1} add send target list"}}'.format(user.id, user.username))
        else:
            target_users_obj.append(user)
            logger.debug('{{"u_id":{0},"action":"get_target_user() '
                         'user {1} add send target list"}}'.format(user.id, user.username))
    return target_users_obj


def get_send_channel(target_users_obj) -> list:
    """
    基于用户列表找到对应的发送渠道
    :param target_users_obj:
    :return:
    """
    # 创建不同的用户消息发送渠道
    # wcd_channel, wc_channel, email_channel, sms_channel, phone_channel = []
    wcd_channel = []
    wc_channel = []
    email_channel = []
    sms_channel = []
    phone_channel = []
    send_channel = [wcd_channel, wc_channel, email_channel, sms_channel, phone_channel]

    # 遍历目标用户,若用户设置了接收策略，则根据设定接收时间把目标用户分配至不同的发送渠道
    for user in target_users_obj:
        # 查询当前用户配置的接收策略，只返回当前时间在设定时间范围内的记录
        receive_rules = ReceiveStrategy.objects.filter(owner=user).filter(
            Q(start__isnull=True) | Q(end__isnull=True) | Q(start__lte=now) | Q(end__gte=now)).filter(
            ~Q(start__gt=now)).filter(~Q(end__lt=now))

        if receive_rules:
            """若接收策略为空，默认使用企业微信渠道发送"""
            for rule in receive_rules:
                # 用户分派到各发送渠道列表
                send_channel[rule.channel].append(user)
        else:
            wc_channel.append(user)
    return send_channel


def send_notification(users, event, msg_type):
    """
    发送通知模块, 基于单个用户对应的发送通道，对时间渲染出来的内容进行发送
    :param users:
    :param event:
    :param msg_type:
    :return:
    """
    # 1. 基于基于user 和 channel 拿到模板
    # 2. event+template 宣讲内容
    # 3. 基于当个用户、内容、渠道进行发送通知
    for i, send_users in enumerate(users):
        """获取对应渠道的发送内容模板"""
        if not send_users:
            # 渠道用户列表若为空，跳出循环
            continue

        data_source = event.ds.name
        # msg_type = event.status

        # 获取不同告警渠道的人员列表信息
        send_users_list = [user.username for user in send_users]
        logger.debug('{{"e_id":"{0}","action":"获取不同告警渠道的人员列表信息. 用户列表:{1}"}}'.format(event.id, send_users_list))
        if not send_users_list:
            continue

        # 获取不同告警渠道的人员列表信息
        send_users_list = [user.username for user in send_users]
        logger.debug('{{"e_id":"{0}","action":"获取不同告警渠道的人员列表信息. 用户列表:{1}"}}'.format(event.id, send_users_list))

        # 获取渠道默认模板
        channel_default_template_object = SendTemplate.objects.filter(channel=i, type=msg_type)
        # 获取数据源模板
        datasource_template_object = channel_default_template_object.filter(ds__name=data_source)
        content = ''
        alert_title = event.name
        content_list = list()

        if datasource_template_object:
            # 通过指定数据源模板渲染发送内容
            content = Template(datasource_template_object.last().content).render({'event': event})
            logger.debug('{{"e_id":"{0}","action":"基于数据源渲染的模板内容{1}"}}'.format(event.id, content))
        elif channel_default_template_object:
            # 通过默认渠道模板渲染发送内容
            content = Template(channel_default_template_object.last().content).render({'event': event})
            logger.debug('{{"e_id":"{0}","action":"默认模板渲染出来的内容{1}" }}'.format(event.id, content))
        elif send_users:
            logger.warning(
                'Message could not be sent cause by no "{0}" template was found in the "{1}" '
                'channel.'.format(TYPE_CHOICES[msg_type][1], RECEIVE_CHOICES[i][1])
            )
        logger.debug('{{"e_id":"{0}","action":"event template to content:{1}"}}'.format(event.id, content))
        # 内容转为字符串
        content_list.append(content)
        alert_content = '\n'.join(content_list)

        alert_channel = [WxAlerter, ItapisWxAlerter, EmailAlerter, SMSAlerter, PhoneAlerter]
        # 获取发送渠道
        alert = alert_channel[i]
        send_result = alert().alert(send_users_list, alert_content, title=alert_title)

        # 发送告警通知人员存入数据库
        if send_result['result']:
            event.receivers.add(*send_users)
            logger.debug('{{"e_id":"{0}", "action":"event add receiver user: {1}"}}'.format(event.id, send_users))
        else:
            logger.error('Notification was sent fail."e_id":"{0}", user: {1}'.format(event.id, send_users))


def create_event(message: object, need_converge: object = None) -> object:
    """
    根据当前消息和收敛类型，创建事件
    :param need_converge:
    :param message: 匹配的多条消息的列表
    """
    # 消息列表
    all_message = []
    if need_converge:
        # 基础收敛规则获取多个消息
        all_message = message.get_burr_messages(need_converge)
        if len(all_message) <= need_converge.count:
            logger.warning('{{"m_id":"{0}","action":"Not enough convergence messages, converge count:{1}, messages '
                           'count:{2}"}}'.format(message.id, need_converge.count, len(all_message)))
            return None
    else:
        # 单个消息创建事件的情况，默认关联第一个消息
        all_message.append(message)
    # 创建事件。事件关联的信息，以消息关联的字段来组装信息。项目和主机host是最小的事件维度。
    event = Event.objects.create(project=message.get_project(),
                                 host=message.host,
                                 name=message.title,
                                 ds=message.get_data_source(),
                                 type=message.type,
                                 converge=need_converge,
                                 level=message.level,
                                 extra=message.extra)

    # 关联告警消息
    event.messages.add(*all_message)
    # todo 使用try的方式判断异常，最后提供一个默认值null
    # 获取关联的分派策略
    delivery = Delivery.objects.filter(project=event.project, parent=None, is_removed=False).last()
    if not delivery:
        logger.warning('{{"e_id":"{0}", "action":"event related delivery is None"}}'.format(event.id))
    # 关联第一层分配策略
    event.current_delivery = delivery
    event.save()
    logger.info('{{"e_id":"{0}","action":"Create event success, name:{1}"}}'.format(event.id, event.name))
    return event


def handle_message_recover(message: Message) -> None:
    """
    处理异常告警恢复
    :param message: 当前事件消息
    """
    events = Event.objects.filter(project__label=message.project, host=message.host, type=message.type,
                                  status__in=STATUS_NOT_CLOSED)
    recovery_event_obj = events.order_by('level').last()
    if recovery_event_obj:
        # 告警恢复消息关联到时间
        recovery_event_obj.messages.add(message)
        # 更新事件为解决状态
        recovery_event_obj.status = STATUS_RESOLVED
        recovery_event_obj.save()
        # 获取所有的已发送人员
        recovery_users_obj = recovery_event_obj.receivers.all()
        # 如果发送人员是否为空
        if recovery_users_obj:
            # 遍历所有关联用户的阻断设置，找到目标用户
            target_users_obj = get_target_user(recovery_users_obj, recovery_event_obj)
            # 遍历所有目标用户的接收策略，把目标用户分配到不同的发送渠道
            send_channel = get_send_channel(target_users_obj)
            # 发送通知给用户
            # title = recovery_event_obj.name
            msg_type = RECOVERY
            send_notification(send_channel, recovery_event_obj, msg_type)
            logger.info(
                '{{"e_id":"{0}","m_id":"{1}","action":"Recovery event success,IP{2} }}'.format(recovery_event_obj.id,
                                                                                           message.id,
                                                                                           recovery_event_obj.host))


@shared_task(ignore_result=True)
def event_close_time_out():
    """事件超时关闭任务"""
    for event in Event.objects.filter(status__in=STATUS_NOT_CLOSED):
        if event.modified <= (timezone.now() - timedelta(minutes=event.ds.close_timeout)):
            event.status = STATUS_TIMEOUT
            event.save()
            logger.info('{{"e_id":"{0}","action":"event time out close, host:{1}"}}'.format(event.id, event.host))


@shared_task(ignore_result=True)
def send_reporter(report_type):
    """ 发送报告模块，日报、周报、月报"""
    reporthandler = ReportHandler()
    reporthandler.send_report_mail_handler(report_type)

