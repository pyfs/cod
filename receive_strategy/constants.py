# 接收通道定义
# todo working 不适合 for sh (暂定)
WECOM = 0
WECHAT = 1
MAIL = 2
MESSAGE = 3
MOBILE = 4

RECEIVE_CHOICES = (
    (WECHAT, '企业微信'),
    (MAIL, '邮箱'),
    (MESSAGE, '短信'),
    (MOBILE, '电话'),
    (WECOM, '微信直通')
)

# 消息类型定义
ALERT = 0
RECOVERY = 1
REPORT = 2

TYPE_CHOICES = (
    (ALERT, '告警'),
    (RECOVERY, '恢复'),
    (REPORT, '报表')
)
