import nonebot
from nonebot import on_command, get_bot
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE_FRIEND
from .get_course import course, get_course_list
from nonebot.params import CommandArg
import re
from datetime import datetime, timedelta
from nonebot import require
from .database_tools import reset_and_insert_today_course, get_db_todays_course_row, del_db_todays_course_row


# 定时任务
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

async def send_message_percourse(lst):
    bot = get_bot()
    text = f'-----下节课程-----'
    text += f'课程名称: {lst[0]}\n'
    text += f'节次: {lst[1]} {lst[2]} ({lst[-1]})\n'
    text += f'授课教师: {lst[5]}\n'
    text += f'地点: {lst[4]}'
    await bot.send_group_msg(group=164264920, message=Message(text))
    del_db_todays_course_row()
    await set_job_scheduled()

@scheduler.scheduled_job("cron", hour="7",minute='00' ,id="daily")
async def run_every_day_7():
    data_list = course.get_by_date(datetime.today().strftime('%m-%d'))
    for lst in data_list:
        if len(lst[3]) == 1:
            lst[3] = str(lst[3])
        else:
            lst[3] = f"{lst[3][0]}-{lst[3][-1]}"
    if data_list:
        text = f"今日课程: {datetime.today().strftime('%m-%d')}\n"
        text += get_send_text(data_list, 1)
        bot = get_bot()
        data_list = [tuple(sublist) for sublist in data_list]
        reset_and_insert_today_course(data_list)
        await bot.send_group_msg(group=164264920, message=Message(text))

def get_send_time():
    """从数据库中获取课程"""
    lst_time = get_db_todays_course_row()
    if lst_time:
        time_str = lst_time[-1].split('-')[0]
        time_str = datetime.strptime(time_str, "%H:%M")
        time_str = time_str - timedelta(minutes=45)
        hours, minutes = str(time_str.hour), str(time_str.minute)
        return hours, minutes, lst_time
    else:
        return '00', '00', None

def set_job_scheduled():
    """设定定时任务"""
    hours, minutes, lst_time = get_send_time()
    if lst_time:
        try:
            scheduler.remove_job('show_next_course')
        except:
            pass
        scheduler.add_job(send_message_percourse, 'cron', hour=hours, minute=minutes, id='show_next_course', args=[lst_time])
    else:
        return

set_job_scheduled()



# 此插件用于汇报课程情况
prior = 30
course_cmd = '课程'
course_aliases = {'课表'}


def args_split(args):
    args.extract_plain_text()
    return str(args)


def get_send_text(info, code):

    text = ''
    le = len(info)
    if code == 1:
        for index, lst in enumerate(info):
            text += f'课程名称: {lst[0]}\n'
            text += f'节次: {lst[1]} {lst[2]} ({lst[-1]})\n'
            text += f'授课教师: {lst[5]}\n'
            text += f'地点: {lst[4]}'
            if index != le - 1:
                text += '\n\n'
        return text
    elif code == 2:
        for index, lst in enumerate(info):
            text += f'课程名称: {lst[0]}\n'
            text += f'节次: {lst[1]} {lst[2]} ({lst[-1]})\n'
            if len(lst[3]) == 1:
                text += f'周次: 第{lst[3]}周 (当前: 第 {course.locate_week()} 周)\n'
            else:
                text += f'周次: {lst[3][0]}-{lst[3][-1]} 周 (当前: 第 {course.locate_week()} 周)\n'
            text += f'授课教师: {lst[5]}\n'
            text += f'地点: {lst[4]}\n'
            text += f'教学班组成: {lst[-3]})\n'
            text += f'学分: {lst[-2]})'
            if index != le - 1:
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
        info, code = get_course_list(datetime.today().strftime('%m-%d'))
    else:
        info, code = get_course_list(args)
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
    course.download_new_pdf()
    await super_handler.finish(Message('Done.'))
