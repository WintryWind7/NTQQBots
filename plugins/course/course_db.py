import asyncio
from tortoise import Tortoise, fields
from tortoise.models import Model

class CourseDB(Model):
    id = fields.IntField(pk=True)  # 主键
    course_name = fields.CharField(max_length=100)  # 课程名称
    week_per = fields.CharField(max_length=10)  # 上课星期
    class_time = fields.CharField(max_length=10)  # 上课时间段，例如“3-4”
    weeks = fields.CharField(max_length=50)  # 上课周次，例如“3-14周”
    location = fields.CharField(max_length=100)  # 上课地点
    teacher = fields.CharField(max_length=50)  # 授课教师
    class_group = fields.CharField(max_length=50)  # 上课班级
    credit = fields.FloatField()  # 学分
    class_period = fields.CharField(max_length=50)  # 上课时段，例如“10:10-11:50”
    weeks_no = fields.CharField(max_length=100)


class TodayCourseDB(Model):
    id = fields.IntField(pk=True)  # 主键
    course_name = fields.CharField(max_length=100)  # 课程名称
    week_per = fields.CharField(max_length=10)  # 上课星期
    class_time = fields.CharField(max_length=10)  # 上课时间段，例如“3-4”
    weeks = fields.CharField(max_length=50)  # 上课周次，例如“3-14周”
    location = fields.CharField(max_length=100)  # 上课地点
    teacher = fields.CharField(max_length=50)  # 授课教师
    class_group = fields.CharField(max_length=50)  # 上课班级
    credit = fields.FloatField()  # 学分
    class_period = fields.CharField(max_length=50)  # 上课时段，例如“10:10-11:50”
    weeks_no = fields.CharField(max_length=100)
