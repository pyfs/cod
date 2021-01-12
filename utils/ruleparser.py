from jsonpath_rw import parse
import json
import re
import logging

logger = logging.getLogger('django')


class RuleParser(object):
    """ 解析过滤规则,输入黑白名单「include, exclude」的方式来具体判断.指定类型，以列表方式来匹配具体规则内容。
        该规则的局限性只能做内容的匹配，不支持逻辑的条件的处理。

        检查rules 格式规范,参考如下
       {"include":
            [
                {"type": ["CP.*", "DI*"]},
                {"host": ["p-login-w-01", "p-zabbix.*"]}
            ],
        "exclude":
            [
                {"type": ["MEM", "file.*"]},
                {"host": ["webserver", "mysql.*"]},
            ]
        }

    """

    def __init__(self, rules, args):
        try:
            self.rules = json.loads(rules)
        except json.JSONDecodeError as e:
            logger.error("Rules is not in JSON format , %s" % e)
        self.args = args

    def check_rule(self):
        for condition in self.rules:
            if isinstance(self.rules[condition], list):
                for sub_con in self.rules[condition]:
                    if isinstance(sub_con, dict) and isinstance(parse('$.*.*').find(sub_con), list):
                        return True
                    else:
                        logger.error('Rule content not default format for [type or host] sub content')
                        return False
            else:
                logger.error('Rule content not default format for [include or exclude]')
        # 获取匹配类型的参数及判断输入内容符合格式,带点分隔，例如 type.CPU
        if not re.findall("\.", self.args):
            logger.error("args wrong format,example:type.CPU")
            return False
        return True

    def processor(self, condition):
        # 检查输入参数和规则的格式规范
        if not self.check_rule():
            return False
        # 检查输入白名单和黑名单的参数
        if condition not in ["include", 'exclude']:
            logger.error("input condition not processor,only:include, exclude")
            return False
        # includes = jsonpath(self.rules, expr='$.{}.*'.format(condition))
        includes = [include.value for include in parse('$.{}.[*]'.format(condition)).find(self.rules)]
        # 拆分类型和匹配的关键字
        filter_type, content = self.args.split('.', 1)
        # 判断类型里面的列表内容，参考格式{"type":["CP.*", "NET*.K"]
        # include_condition = jsonpath(includes, expr='$.*.{}.*'.format(filter_type))
        include_condition = parse('$.[*].{}'.format(filter_type)).find(includes)

        if include_condition:
            # 匹配输入条件和过滤规则，如果匹配中的情况添加到列表,最后判断列表内容返回值
            result = list(filter(lambda x: re.match(x, content) is not None, include_condition[0].value))
            if result:
                return True
            else:

                logger.warning("No matching filter conditions")
                return False
        else:
            logger.warning("No matching filter conditions")
            return include_condition

# data = {"include":
#             [
#                 {"type": [".*U"]},
#                 {"host": ["NETWORK", "IP"]}
#             ],
#         "exclude":
#             [
#                 {"type": ["MEM", "TEST"]},
#                 {"host": ["DD", "GOGO"]},
#             ]
#         }
# str_data: str = json.dumps(data)
# handle = RuleParser(rules=str_data, args='type.CPU')
# if handle.processor('include'):
#     print("include")
# else:
#     print("exclude")
