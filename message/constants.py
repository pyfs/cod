# 告警级别
LEVEL_WARNING = 0
LEVEL_DANGER = 1
LEVEL_DISASTER = 2

LEVEL_CHOICES = (
    (LEVEL_WARNING, '警告'),
    (LEVEL_DANGER, '危险'),
    (LEVEL_DISASTER, '灾难')
)
# 需要升级的告警级别
LEVEL_NEED_UPGRADE = [1, 2]

# 针对告警类型重复发给用户,避免遗漏严重的告警类型
LOOP_UPGRADE = [2]

# 告警消息状态
STATUS_ALERT = 'alert'
STATUS_RECOVER = 'recover'

# 用户规则类型
RULE_TYPES = ['name', 'project', 'host', 'level', 'type', 'ds']
