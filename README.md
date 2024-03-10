# NTQQBots

本项目基于 [LLOneBot](https://github.com/LLOneBot/LLOneBot)，官方NTQQ插件 [LiteLoaderQQNT](https://liteloaderqqnt.github.io/)，以及python框架[nonebot2](https://github.com/nonebot/nonebot2?tab=readme-ov-file)。

使用 [OneBotv11](https://onebot.dev/) 标准，设置NTQQ内反向 websocket 监听：

 `ws://127.0.0.1:8080/onebot/v11/`

## 环境配置方法

```bash
pip install nonebot
```

```bash
pip install nb-cli
```

```bash
nb adapter install nonebot-adapter-onebot
```

```bash
nb driver install nonebot2[fastapi]
```

## 导入插件

```python
nonebot.load_plugins("plugins")
```

## 插件编写

`https://nonebot.dev/docs/api/`

#### 超级用户

```.env
SUPERUSERS=["console_user"]
```

```python
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE_FRIEND
```

```python
# 创建消息处理器，响应私聊消息
msg_handler = on_message(rule=to_me(), permission=SUPERUSER, )

@msg_handler.handle()
async def handle_private_msg(bot: Bot, event: PrivateMessageEvent, state: T_State):

    msg_content = str(event.get_message())
    await msg_handler.finish(Message("我收到你的表情了！"))
```

