项目: Cod
维护: peizhenfei
邮箱: peizhenfei@cvte.com

> ### 项目简介
基于告警消息收敛为事件，以其为核心进行多维度的策略管制的告警平台。

## 环境变量设置

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

## 初始化开发环境
根目录下面有一个Makefile文件，具体详情可以看里面写了什么。初始化环境需要执行如下命令：
> make clean  &&  make make
> 提示设置管理员的密码

## 配置rabbitmq
> 进入项目目录里面的docker-compose/rabbitmq  
> 启动rabbitmq环境 docker-compose up -d


## 业务环境配置操作指引
### 1、增加数据源
### 2、增加密钥
### 3、增加项目
### 4、推送消息到接口调试
#### 推送消息测试用

```bash
#!/bin/bash
NUB=$3
STA=$2
PRO=$1
NOWTIME=`date '+%Y-%m-%d %H:%M:%S'`
#type=HostHighCpuLoad
curl --location --request POST 'http://127.0.0.1:8000/api/v1/message/restapi/?token=f24be027127a47c989971743a1601406' \
--form "project=$1" \
--form "type=HostHighCpuLoad" \
--form "host=10.20.30.$NUB" \
--form "title=MemoryVeryHight 10.22.23.$NUB" \
--form "level=0" \
--form "status=$STA" \
--form "created=$NOWTIME"
```
> sh push_msg.sh CLOUD alert 16
