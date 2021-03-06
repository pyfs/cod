"""
.envrc 文件是 direnv 项目的配置文件
Env类优先读取 .envrc 中的配置，再读取环境变量的配置
"""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Env(object):
    """文件格式"""
    DATA = dict()
    SOURCES = [os.environ, DATA]

    def __init__(self, file_path: str = None) -> None:
        """
        从文件中读取环境变量
        :param file_path: 文件路径,默认为项目目下 .envrc
        """
        default_file = os.path.join(BASE_DIR, '.envrc')
        file_path = file_path or default_file

        # 兼容文件不存在的情况
        if os.path.exists(file_path):
            with open(file_path) as f:
                for line in f.readlines():
                    # 警号注释支持
                    if line.startswith('#'):
                        continue
                    kv = line.split()[1].split('=')
                    self.DATA[kv[0].strip()] = kv[1].strip()
        else:
            print("[warning]: envrc (%s) not exist, please check" % file_path)

    def get(self, key: str, default: str = None) -> str:
        """
        获取环境变量值
        :param key: 环境变量 key
        :param default: 默认值
        :return: value
        """
        value = None
        for source in self.SOURCES:
            value = source.get(key)
            if value:
                break
        return value or default
