import nonebot
import asyncio
from nonebot import on_command, get_bot
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE_FRIEND
from nonebot.params import CommandArg
import re
from datetime import datetime, timedelta
from nonebot import require
from .course_db_init import db_init
asyncio.run(db_init())

from .course_db import CourseDB, TodayCourseDB
from typing import List, Tuple
from .get_course import course, get_course_list, get_course_by_str
from nonebot import logger


# 定时任务
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

# 此插件用于汇报课程情况
prior = 30
course_cmd = '课程'
course_aliases = {'课表'}


async def send_message_percourse(co:TodayCourseDB):
    bot = get_bot()
    text = f'-----下节课程-----\n'
    text += f'课程名称: {co.course_name}\n'
    text += f'节次: {co.week_per} {co.class_time} ({co.class_period})\n'
    text += f'授课教师: {co.teacher}\n'
    text += f'地点: {co.location}'
    await bot.send_group_msg(group_id=164264920, message=Message(text))
    await set_job_scheduled()

# @scheduler.scheduled_job("cron", hour="6",minute='50' ,id="daily0")
# async def get_new_course_table():
#     if course.get_new_course_table():
#         await course.update()
#     else:
#         logger.error('更新课表失败！')



@scheduler.scheduled_job("cron", hour="7",minute='00', id="daily")
async def run_every_day_7():
    await course.update_today_courses()
    bot = get_bot()
    course_list = await TodayCourseDB.all()
    if course_list:
        date_obj = datetime.today()
        week = '周' + ['一', '二', '三', '四', '五', '六', '日'][date_obj.weekday()]
        text = f"今日课程: {datetime.today().strftime('%m-%d')} 第{course.locate_week()}周 {week}\n"
        text += get_send_text(course_list, 1)
        await set_job_scheduled()
        await bot.send_group_msg(group_id=164264920, message=Message(text))
    else:
        await bot.send_group_msg(group_id=164264920, message=Message(f"今日：{datetime.today().strftime('%m-%d')} 没有课程 ^.^..."))


async def get_send_time():
    """从数据库中获取课程"""
    lst:TodayCourseDB = await TodayCourseDB.first()
    while lst:
        time_str = lst.class_period.split('-')[0]
        time_str = datetime.strptime(time_str, "%H:%M")
        time_str = time_str - timedelta(minutes=45)
        hours, minutes = str(time_str.hour), str(time_str.minute)
        await lst.delete()
        if datetime.now().time() > time_str.time():
            lst: CourseDB = await TodayCourseDB.first()
            continue
        return hours, minutes, lst
    else:
        return '00', '00', None

async def set_job_scheduled():
    """设定定时任务"""
    hours, minutes, lst = await get_send_time()
    if lst:
        try:
            scheduler.remove_job('show_next_course')
        except:
            pass
        scheduler.add_job(send_message_percourse, 'cron', hour=hours, minute=minutes, id='show_next_course', args=[lst])
    else:
        return

asyncio.run(set_job_scheduled())

def args_split(args):
    args.extract_plain_text()
    return str(args)


def get_send_text(info:List[CourseDB], code:int):

    text = ''
    if isinstance(info, list):
        le = len(info)
    else:
        le = 1
    if code == 1:
        i = 0
        for co in info:
            text += f'课程名称: {co.course_name}\n'
            text += f'节次: {co.week_per} {co.class_time} ({co.class_period})\n'
            text += f'授课教师: {co.teacher}\n'
            text += f'地点: {co.location}'
            i += 1
            if i != le:
                text += '\n\n'
        return text
    elif code == 2:
        i = 0
        for co in info:
            text += f'课程名称: {co.course_name}\n'
            text += f'节次: {co.week_per} {co.class_time} ({co.class_period})\n'
            if len(co.weeks_no) == 1:
                text += f'周次: 第{co.weeks_no}周 (当前: 第 {co.weeks_no} 周)\n'
            else:
                text += f'周次: {co.weeks} (当前: 第 {course.locate_week()} 周)\n'
            text += f'授课教师: {co.teacher}\n'
            text += f'地点: {co.location}\n'
            text += f'教学班组成: {co.class_group})\n'
            text += f'学分: {co.credit})'
            i += 1
            if i != le:
                text += '\n\n'
        return text
    else:
        return '踏马的又出bug了！'


msg_handler = on_command(cmd=course_cmd,
                                    aliases=course_aliases,
                                    rule=None,
                                    permission=PRIVATE_FRIEND|GROUP,
                                    priority=prior,
                                    block=True)
@msg_handler.handle()
async def handle_private_msg(bot: Bot, event, state: T_State, args: Message = CommandArg()):
    if isinstance(event, GroupMessageEvent):    # 群聊
        pass
    elif isinstance(event, PrivateMessageEvent):  # 私聊
        pass
    args = args_split(args)  # /cmd [date, week, others]

    if args=='':
        info, code = await get_course_by_str(datetime.today().strftime('%m-%d'))
    else:
        info, code = await get_course_by_str(args)
    if info:
        text = get_send_text(info, code)
        await msg_handler.finish(Message(text))
    await msg_handler.finish(Message("暂未查询到课程。"))


super_handler = on_command(cmd=('课程', '更新'),
                            aliases={('课表', '更新')},
                            rule=None,
                            permission=SUPERUSER,
                            priority=prior-2,
                            block=True)
@super_handler.handle()
async def handle_private_msg(bot: Bot, event, state: T_State, args: Message = CommandArg()):
    # if course.get_new_course_table():
    #     await course.update()
    # else:
    #     logger.error('更新大课表失败！')
    await course.update()
    await course.update_today_courses()
    await set_job_scheduled()
    await super_handler.finish(Message('Done.'))

    # except:
    #     await super_handler.finish(Message('Error...'))


super_handler_test = on_command(cmd=('测试'),
                            rule=None,
                            permission=SUPERUSER,
                            priority=prior-2,
                            block=True)
@super_handler_test.handle()
async def handle_private_msg(bot: Bot, event, state: T_State, args: Message = CommandArg()):
    print('-----测试-----')
