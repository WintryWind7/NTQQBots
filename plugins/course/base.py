import os
from datetime import datetime, timedelta
import re
import fitz


def current_path(*args) -> str:
    """准确的路径"""
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(current_script_path, *args)
    return data_file_path


def locate_week(input_date_str=datetime.now().strftime("%m-%d")) -> int:
    """获取当前是第几周"""

    start_date = datetime(2024, 2, 26)
    input_year = start_date.year
    input_date = datetime.strptime(f"{input_year}-{input_date_str}", "%Y-%m-%d")

    day_diff = start_date.weekday()  # 周一是weekday() == 0
    if day_diff != 0:
        start_date -= timedelta(days=day_diff)
    first_week_end = start_date + timedelta(days=6)

    if input_date <= first_week_end:
        week_number = 1
    else:
        days_after_first_week = (input_date - first_week_end - timedelta(days=1)).days
        week_number = (days_after_first_week // 7) + 2

    return int(week_number)


def find_info_by_pattern(lst, pattern1, pattern2=None):
    """在列表中查找匹配给定正则表达式模式的信息。
    可以接受两个查询，第一个没有则执行第二个，没有则返回None"""

    compiled_pattern1 = re.compile(pattern1)
    if pattern2:
        compiled_pattern2 = re.compile(pattern2)

    for item in lst:
        match = compiled_pattern1.search(item)
        if match:
            return match.group()
    if pattern2:
    # 如果第一个模式没有匹配到，尝试匹配第二个模式
        for item in lst:
            match = compiled_pattern2.search(item)
            if match:
                return match.group()

    return None

def find_matching_index(lst, pattern):
    """遍历列表，寻找第一个匹配给定模式的项的索引。"""
    compiled_pattern = re.compile(pattern)

    for index, text in enumerate(lst):
        if compiled_pattern.search(text):
            return index

    return None


def check_both_time_course(lst):
    c = find_matching_index(lst, '学分:')
    if len(lst)-c > 4:
        return c
    else:
        return None


def check_place_is_normal(place):
    pattern_places = ['资讯楼', '知善楼', '交流中心', '知信楼', '行健楼', '行远楼', '轨道交通实训基地', '科技园']
    for pattern_place in pattern_places:
        if pattern_place in place:
            return 1
    return None

mapping01 = {
    '5': '13:30',
    '6': '14:25',
    '7': '15:30',
    '8': '16:25',
    '9': '18:00',
    '10': '18:50',
    '11': '19:40',
}

mapping02 = {
    '5': '14:15',
    '6': '15:10',
    '7': '16:15',
    '8': '17:10',
    '9': '18:45',
    '10': '19:35',
    '11': '20:25',
}


mapping01_1 = {
    '3': '10:10',
    '4': '11:05',
}

mapping01_2 = {
    '3': '9:55',
    '4': '10:50',
}

mapping02_1 = {
    '3': '10:55',
    '4': '11:50',
}

mapping02_2 = {
    '3': '10:40',
    '4': '11:35',
}
def change_time_to_daytime(lst):
    """基于索引，将节次转为时间"""
    time = lst[3]
    if len(time) <3 :
        time += '-' + time

    start_time = None
    end_time = None

    day_time = time.split('-')
    if day_time[0] == '1':
        if lst[2][-1] == '六' or lst[2][-1] == '日':
            start_time = '8:30'
        else:
            start_time = '8:00'
    if day_time[1] == '1':
        if lst[2][-1] == '六' or lst[2][-1] == '日':
            end_time = '9:15'
        else:
            end_time = '8:45'

    if day_time[0] == '2':
        if lst[2][-1] == '六' or lst[2][-1] == '日':
            start_time = '9:25'
        else:
            start_time = '8:55'
    if day_time[1] == '2':
        if lst[2][-1] == '六' or lst[2][-1] == '日':
            end_time = '10:10'
        else:
            end_time = '9:40'
    if not start_time:
        if day_time[0] in mapping01:
            start_time = mapping01[day_time[0]]
        else:
            if check_place_is_normal(lst[5]) or (lst[2][-1] == '六' or lst[2][-1] == '日'):
                start_time = mapping01_1[day_time[0]]
            else:
                start_time = mapping01_2[day_time[0]]
    if not end_time:
        if day_time[1] in mapping02:
            end_time = mapping02[day_time[1]]
        else:
            if check_place_is_normal(lst[5]) or (lst[2][-1] == '六' or lst[2][-1] == '日'):
                end_time = mapping02_1[day_time[1]]
            else:
                end_time = mapping02_2[day_time[1]]

    return start_time + '-' + end_time

# === re  end=====

# === get_course_list start====
def get_course_list():
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


def str_week_no(week_no):
    return '.' + str(week_no) + '.'


