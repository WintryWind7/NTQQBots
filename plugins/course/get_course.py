import fitz
import os
import re
from datetime import datetime, timedelta
import shutil
import requests
from nonebot import logger
from .base import current_path, locate_week, find_info_by_pattern, get_course_list, str_week_no
import sqlite3
import asyncio
from .course_db import CourseDB, TodayCourseDB
from .selenium_tools import download_pdf


# === class Course start===

class Course(object):

    def __init__(self):
        self.weeks_no = []

    async def update(self):
        await CourseDB.all().delete()
        course_list = get_course_list()
        for course in course_list:
            await CourseDB.create(
                id=course[0],
                course_name=course[1],
                week_per=course[2],
                class_time=course[3],
                weeks=course[4],
                location=course[5],
                teacher=course[6],
                class_group=course[7],
                credit=course[8],
                class_period=course[9],
                weeks_no=self.process_weeks(course[4]),
            )
        logger.success("新的课程表数据添加成功！")

    async def get_by_course_name(self, course_name):
        """按名称查询，没有周数要求，正常返回列表"""
        matched_courses = await CourseDB.filter(course_name__icontains=course_name)
        return matched_courses

    async def get_by_week_per(self, week_per, week_no=locate_week()):
        """按节次/周查询课程，返回匹配的课程列表。"""
        matched_courses = await CourseDB.filter(weeks_no__contains=str_week_no(week_no), week_per=week_per)
        return matched_courses

    async def get_by_week_no(self, week_no=locate_week()):
        """根据周次查询课程，返回在该周次有安排的课程列表。"""
        matched_courses = await CourseDB.filter(weeks_no__contains=str_week_no(week_no))
        return matched_courses

    async def get_by_teacher_name(self, teacher_name):
        """根据授课教师查询，返回在该周次有安排的课程列表。"""
        matched_courses = await CourseDB.filter(teacher__icontains=teacher_name)
        return matched_courses

    async def get_by_place_name(self, place):
        """根据周次查询课程，返回在该周次有安排的课程列表。"""
        matched_courses = await CourseDB.filter(location__icontains=place)
        return matched_courses

    async def get_by_date(self, date_str):
        """根据日期查询课程，返回在该日期有安排的课程列表。"""
        week_no = locate_week(date_str)  # 使用locate_week确定周次
        date_obj = datetime.strptime(f"2024-{date_str}", "%Y-%m-%d")  # 假设年份为2024年
        week_day = '周' + ['一', '二', '三', '四', '五', '六', '日'][date_obj.weekday()]  # 确定星期几
        matched_courses = await CourseDB.filter(weeks_no__contains=str_week_no(week_no), week_per=week_day)
        return matched_courses

    async def update_today_courses(self):
        await TodayCourseDB.all().delete()

        course_list = await self.get_by_date(datetime.today().strftime('%m-%d'))

        for i, course in enumerate(course_list):
            await TodayCourseDB.create(
                id=i,
                course_name=course[1],
                week_per=course[2],
                class_time=course[3],
                weeks=course[4],
                location=course[5],
                teacher=course[6],
                class_group=course[7],
                credit=course[8],
                class_period=course[9],
                weeks_no=self.process_weeks(course[4]),
            )
        logger.success('今日课程表更新成功！')

    def get_new_course_table(self):
        if download_pdf():
            return True
        else:
            return False

    def process_weeks(self, text):
        if len(text[:-1]) < 3:
            return [int(text[:-1])]
        num_lst = text[:-1].split('-')
        a, b = int(num_lst[0]), int(num_lst[1])
        lst = list(range(a, b + 1))

        return '.' + '.'.join(map(str, lst)) + '.'

    def locate_week(self):
        return locate_week()



date_mapping = {
    '昨天': -1,
    '前天': -2,
    '今天': 0,
    '明天': 1,
    '后天': 2,
    '大后天': 3,
}

async def get_course_by_str(search_str: str):
    """根据所给的信息获取课程信息"""
    if re.compile(r'^\d{2}-\d{2}$').match(search_str):   # 判断是否符合日期格式
        return await course.get_by_date(search_str), 1

    if search_str in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
        return await course.get_by_week_per(search_str), 1

    if search_str in date_mapping.keys():
        date = datetime.today() + timedelta(days=date_mapping[search_str])
        return await course.get_by_date(date.strftime('%m-%d')), 1

    if re.findall(r'上|下', search_str):
        offset_week = locate_week()

        matches = re.findall(r'上|下', search_str)
        for match in matches:
            if match == '上':
                offset_week -= 1
            elif match == '下':
                offset_week += 1

        str_input = re.sub(r'上|下', '', search_str)
        if str_input in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
            return await course.get_by_week_per(str_input, offset_week), 1

    teacher_courses = await course.get_by_teacher_name(search_str)
    if teacher_courses:
        return teacher_courses, 2

    course_name_courses = await course.get_by_course_name(search_str)
    if course_name_courses:
        return course_name_courses, 2

    place_name_courses = await course.get_by_place_name(search_str)
    if place_name_courses:
        return place_name_courses, 2

    return None, None


course = Course()
async def main():
    await course.update()

asyncio.run(main())

if __name__ == "__main__":
    print(locate_week())


