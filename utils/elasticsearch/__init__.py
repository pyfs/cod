import logging

from elasticsearch_dsl.connections import create_connection
from elasticsearch_dsl import Search, Document
from elasticsearch_dsl import Date, Nested, Boolean, analyzer, Completion, Keyword, Text, Integer
from datetime import datetime, timezone

from utils.env import Env

env = Env()

ES_HOST = env.get('ES_HOST')
ES_PORT = env.get('ES_PORT')
ES_USERNAME = env.get('ES_USERNAME')
ES_PASSWORD = env.get('ES_PASSWORD')
ES_INDEX = env.get('ES_INDEX')

logger = logging.getLogger('django')


class InitES(Document):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # todo 连接池、连接探测检查
        create_connection(hosts=['{0}:{1}'.format(ES_HOST, ES_PORT)],
                          http_auth="{0}:{1}".format(ES_USERNAME, ES_PASSWORD), timeout=20)

        @staticmethod
        def check_data(data):
            if not isinstance(data, dict):
                return False
            # 检查写入es的关键字段内容,部分字段内容提供默认值
            time_type_key = ["createtime", "updatetime"]
            str_type_key = ["env", "type", "id", "period", "tags", "users"]
            # 添加默认时间字段
            for key in time_type_key:
                if key not in data.keys():
                    data[key] = datetime.now()
            # 判断字段类型, 处理异常情况
            for key in data.keys():
                # 检查Key的类型
                if key in time_type_key:
                    if isinstance(data[key], datetime):
                        data[key] = datetime.now()
                    else:
                        logger.warning("Data is not the default type, key set datetime.now {0}".format(key))
                elif key in str_type_key:
                    if isinstance(data[key], str):
                        continue
                    else:
                        key = str(data[key])
                        logger.warning("Data is not the default type, try str(key), {0}".format(key))
                elif key == "content":
                    if isinstance(data[key], dict):
                        data[key] = str(data[key])
                    else:
                        data[key] = str(data[key])
                        logger.warning("Data is not the default type, try dict(key), {0}".format(key))
                else:
                    logger.warning("Data is not the default key, please check key, {0}".format(key))
            return True
