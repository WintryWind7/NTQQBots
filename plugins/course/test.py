import fitz
import os
import re
from datetime import datetime, timedelta
import requests
from get_course import Course, get_new_course

course = Course(get_new_course())
date_mapping = {
    '昨天': -1,
    '前天': -2,
    '今天': 0,
    '明天': 1,
    '后天': 2,
    '大后天': 3,
}
def get_course_list(str:str):
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

data_list = course.get_by_date(datetime.today().strftime('%m-%d'))


print(data_list)
