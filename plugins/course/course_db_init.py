import asyncio
import time

from tortoise import Tortoise
from .base import current_path
from nonebot import logger

TORTOISE_ORM = {
    "connections": {
        "default": f"sqlite://{current_path('data', 'course.db')}",
        # 对于其他数据库，你可能需要提供不同的连接字符串
        # 例如 PostgreSQL: "postgres://user:password@localhost:5432/mydatabase"
        # MySQL: "mysql://user:password@localhost/mydatabase"
    },
    "apps": {
        "course": {
            "models": ["plugins.course.course_db"],  # 或者是你的模型所在的模块路径
            "default_connection": "default",
        },
    },
}

async def db_init():
    # 初始化 Tortoise ORM
    await Tortoise.init(config=TORTOISE_ORM)
    logger.success('数据库初始化完成！')
    # 生成数据库模式
    await Tortoise.generate_schemas()


