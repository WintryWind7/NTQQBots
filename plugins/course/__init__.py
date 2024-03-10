from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, PrivateMessageEvent, GroupMessageEvent
from nonebot.rule import to_me, Rule
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.permission import GROUP, PRIVATE_FRIEND
from .get_course import get_new_course, Course
from nonebot.params import CommandArg
import re
from datetime import datetime, timedelta

course = Course(get_new_course())

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
        for index, course in enumerate(info):
            text += f'课程名称: {course[0]}\n'
            text += f'节次: {course[1]} {course[2]} ({course[-1]})\n'
            text += f'授课教师: {course[5]}\n'
            text += f'地点: {course[4]}'
            if index != le - 1:
                text += '\n\n'
        return text
    elif code == 2:
        for index, course in enumerate(info):
            text += f'课程名称: {course[0]}\n'
            text += f'节次: {course[1]} {course[2]} ({course[-1]})\n'
            if len(course[3]) == 1:
                text += f'周次: 第{course[3]}周 (当前: 第 {course.locate_week()} 周)\n'
            else:
                text += f'周次: {course[3][0]}-{course[3][-1]} 周 (当前: 第 {course.locate_week()} 周)\n'
            text += f'授课教师: {course[5]}\n'
            text += f'地点: {course[4]}'
            text += f'教学班组成: {course[-3]})\n'
            text += f'学分: {course[-2]})\n'
            if index != le - 1:
                text += '\n\n'
        return text
    else:
        return '踏马的又出bug了！'

date_mapping = {
    '昨天': -1,
    '前天': -2,
    '今天': 0,
    '明天': 1,
    '后天': 2,
    '大后天': 3,
}

def get_course(str:str):
    """根据所给的信息获取课程信息"""
    if re.compile(r'^\d{2}-\d{2}$').match(str):   # 判断是否符合日期格式
        return course.get_by_date(str), 1

    if str in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
        return course.get_by_week_per(str), 1

    if str in date_mapping.keys():
        date = datetime.today() + timedelta(days=date_mapping[str])
        return course.get_by_date(date.strftime('%m-%d')), 1

    if re.findall(r'上|下', str):
        offset_week = course.locate_week()

        matches = re.findall(r'上|下', str)
        for match in matches:
            if match == '上':
                offset_week -= 1
            elif match == '下':
                offset_week += 1

        str_input = re.sub(r'上|下', '', str)
        if str_input in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
            return course.get_by_week_per(str_input, offset_week), 1

    if course.get_by_teacher_name(str):
        return course.get_by_teacher_name(str), 2

    if course.get_by_course_name(str):
        return course.get_by_course_name(str), 2

    if course.get_by_place_name(str):
        return course.get_by_place_name(str), 2

    return None, None


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
        info, code = get_course(datetime.today().strftime('%m-%d'))
    else:
        info, code = get_course(args)
    if info:
        text = get_send_text(info, code)
        await msg_handler.finish(Message(text))
    await msg_handler.finish(Message("暂未查询到课程。"))

super_handler = on_command(cmd=('课程', '更新'),
                            aliases=('课表', '更新'),
                            rule=None,
                            permission=SUPERUSER,
                            priority=prior-2,
                            block=True)
@super_handler.handle()
async def handle_private_msg(bot: Bot, event, state: T_State, args: Message = CommandArg()):
    course.download_new_pdf()
    await super_handler.finish(Message('Done.'))
