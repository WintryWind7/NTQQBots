import os
from plugins.course.get_course import main, change_time_to_daytime, check_both_time_course
from plugins.course.base import current_path, find_info_by_pattern
import re
import fitz

def main():
    """根据pdf文件提取出最原始的课程列表"""

    path = [file for file in os.listdir(current_path('data')) if file.endswith('.pdf')]
    doc = fitz.open(current_path('data', path[0]))

    text = ''
    for page in doc:
        text += page.get_text()
    text = re.split(r'(星期[一二三四五六日])', text)

    daily_courses = {}
    current_day = None

    for item in text:
        if item.startswith("星期"):
            current_day = item  # 更新当前处理的天
            daily_courses[current_day] = []  # 初始化当前天的课程列表
        elif current_day:
            daily_courses[current_day].append(item)   # 添加课程信息到当前天

    # 真实课程字典
    current_courses = {}
    course_infos = []
    for key, value in daily_courses.items():
        text = str(value[0]).strip().replace('\n', ',')
        text = text.replace('◎', '')
        text = text.replace('◆', '')
        text = re.sub(r':\s+', ':', text)
        # text = re.sub(r'\s+', ',', text)
        c_ls = text.split(',')
        pattern = re.compile(r'^\d+-\d+$')
        # 判断是否有 数字-数字 的组合
        matches_indexs = [index for index, item in enumerate(c_ls) if pattern.match(item)]


        for i in range(len(matches_indexs) - 1):
            start_index = matches_indexs[i]
            end_index = matches_indexs[i + 1]
            course_info = [key] + c_ls[start_index:end_index]
            course_infos.append(course_info)

        # 最后的课程片段
        last_course_info = [key] + c_ls[matches_indexs[-1]:]
        course_infos.append(last_course_info)

    current_course_infos = []
    # 执行同节次课程检查
    for course in course_infos:
        idx = check_both_time_course(course)
        if idx:
            current_course_infos.append(course[:idx+1])
            current_course_infos.append([course[0]] + [course[1]] + course[idx+1:])
        else:
            current_course_infos.append(course)

    deln = None
    for index, words in enumerate(current_course_infos):
        for lst in words:
            for word in lst:
                if word.find('其他课程'):
                    deln = index
                    break
    current_course_infos.pop(deln)

    course_list = []
    for index, course in enumerate(current_course_infos):
        current_list = []
        current_list.append(index)
        current_list.append(course[2])  # 课程名称
        current_list.append(course[0].replace('星期', '周'))  # 节次/周
        current_list.append(course[1])  # 节次/日
        current_list.append(find_info_by_pattern(course, r"周数:\d+-\d+周", r'周数:\d+周')[3:])   # 周次
        current_list.append(find_info_by_pattern(course, r"地点:[^\s]+")[3:])  # 地点
        current_list.append(find_info_by_pattern(course, r"教师:[^\s]+")[3:])  # 授课老师
        current_list.append(find_info_by_pattern(course, r"教学班组成:[^\s]+")[6:])  # 教学班组成
        current_list.append(find_info_by_pattern(course, r"学分:[^\s]+")[3:])  # 学分
        current_list.append(change_time_to_daytime(current_list))  # 准确节次
        course_list.append(current_list)

    return course_list