# :alarm_clock: Call of Duty 使命召唤

接收告警消息并根据收敛策略合并为事件，并围绕告警事件，在告警产生和告警到达之间展开业务逻辑。
减少重复告警消息的打扰，让每条告警都得到处理！

无监控，不运维；无告警，很开心！

# :construction_worker: 项目维护
项目管理: 裴振飞

项目主程: 刘生华，简佳俊，裴振飞

联系邮箱: peizhenfei@cvte.com

# :rocket: 项目进度


```mermaid
gantt
    title COD 项目规划进度 2021-01 ~ 2021-03
    dateFormat  YYYY-MM-DD
    excludes Saturdayt, Sunday
    todayMarker stroke-width:5px,opacity:0.7

    section 后端开发
    健康日报功能开发    :report, 2020-12-05, 2021-01-30

    section 部署支持
    s2i-python-container   :s2i-python-container, 2021-01-04, 2021-01-08
    优化 CD 构建速度   :after s2i-python-container, 2021-01-31

    section 文档补全
    安装部署文档    :active, 2021-01-13, 2021-01-31
    春节假期    : holiday, 2021-02-11, 2021-02-17
    核心代码逻辑文档    :code, 2021-02-01, 2021-02-28
    使用说明文档    :after code, 2021-03-31
    
    section 开源进度
    去掉单点登录及发送通道  :opensource, 2021-03-01, 2021-03-31
```

<details>
<summary>COD 项目规划进度: 2020-11 ~ 2020-12</summary>

```mermaid
gantt
    title COD 项目规划进度 2020-11 ~ 2020-12
    dateFormat  YYYY-MM-DD
    excludes Saturdayt, Sunday
    todayMarker stroke-width:5px,opacity:0.7

    section 后端开发
    主逻辑上线 V1.0    :masterv1, 2020-10-26, 2020-11-30
    上线后异常处理      :after masterv1, 2020-12-30
    对接 Prometheus，鲸云，Zabbix 等    :datasource, 2020-11-01, 2020-11-29
    健康日报功能开发    :report, 2020-12-05, 2020-12-30

    section 部署支持
    kubesphere 2.2.1 升级到 3.1.0   :ksv2->v3, 2020-11-05,2020-11-20
    s2i-centos-django   :s2i-centos-django, 2020-11-18, 2020-11-28
    CICD 优化   :after s2i-centos-django, 2020-12-30
```

</details>


# 项目部署

- [ ] 部署文档待补全

# :speech_balloon: 环境变量说明

```
# cat .envrc
export RUN_ENV=DEVELOP
export SECRET_KEY=!!!secret-key-must-be-changed!!!
CELERY_BROKER_URL=!!!amqp://user:password@host:port/vhost!!!
export DB_NAME=!!!data-base-name!!!
export DB_HOST=!!!data-base-host!!!
export DB_PORT=!!!data-base-host-port!!!
export DB_USERNAME=!!!data-base-user-name!!!
export DB_PASSWORD=!!!data-base-password!!!
```

# :beer: 参与开发

- [ ] 开发文档待补全

# :question: 如有疑问

任何疑问，可直接提 ISSUE 给我们，描述清楚问题，我们会尽快给予回复！