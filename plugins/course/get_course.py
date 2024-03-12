import fitz
import os
import re
from datetime import datetime, timedelta
import shutil
import requests
from nonebot import logger


def current_path(*args):
    """用于获取准确的目录"""
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(current_script_path, *args)
    return data_file_path

# === datetime start===
def locate_week(input_date_str=datetime.now().strftime("%m-%d")):
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

    return week_number

# print(locate_week('03-04'))

# === datetime end===

# === csv start===
import csv
def list_to_csv_with_index(data, file_name):
    """将多维列表转换为CSV文件。"""
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Index'] + ['课程名', '节次/周', '节次/日', '周次', '上课地点', '授课教师', '教学班组成', '学分', '具体时间'])
        for index, row in enumerate(data, start=1):
            writer.writerow([index] + row)

# === csv end====

# === re start====
def find_matching_index(lst, pattern):
    """遍历列表，寻找第一个匹配给定模式的项的索引。"""
    compiled_pattern = re.compile(pattern)

    for index, text in enumerate(lst):
        if compiled_pattern.search(text):
            return index

    return None


def find_info_by_pattern(lst, pattern1, pattern2=None):
    """在列表中查找匹配给定正则表达式模式的信息。"""

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
    # 将节次转化为具体时间
    time = lst[2]
    if len(time) <3 :
        time += '-' + time

    start_time = None
    end_time = None

    day_time = time.split('-')
    if day_time[0] == '1':
        if lst[1][-1] == '六' or lst[1][-1] == '日':
            start_time = '8:30'
        else:
            start_time = '8:00'
    if day_time[1] == '1':
        if lst[1][-1] == '六' or lst[1][-1] == '日':
            end_time = '9:15'
        else:
            end_time = '8:45'

    if day_time[0] == '2':
        if lst[1][-1] == '六' or lst[1][-1] == '日':
            start_time = '9:25'
        else:
            start_time = '8:55'
    if day_time[1] == '2':
        if lst[1][-1] == '六' or lst[1][-1] == '日':
            end_time = '10:10'
        else:
            end_time = '9:40'
    if not start_time:
        if day_time[0] in mapping01:
            start_time = mapping01[day_time[0]]
        else:
            if check_place_is_normal(lst[4]) or (lst[1][-1] == '六' or lst[1][-1] == '日'):
                start_time = mapping01_1[day_time[0]]
            else:
                start_time = mapping01_2[day_time[0]]
    if not end_time:
        if day_time[1] in mapping02:
            end_time = mapping02[day_time[1]]
        else:
            if check_place_is_normal(lst[4]) or (lst[1][-1] == '六' or lst[1][-1] == '日'):
                end_time = mapping02_1[day_time[1]]
            else:
                end_time = mapping02_2[day_time[1]]

    return start_time + '-' + end_time

# === re  end=====

# === main start====
def main():

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
    for course in current_course_infos:
        current_list = []
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


def get_new_course():
    course_list = main()
    list_to_csv_with_index(course_list, current_path('data', 'course.csv'))
    return course_list

# === main end====

class Course(object):

    def __init__(self, course_list):
        self.course_list = []
        for course in course_list:
            self.course_list.append(self.preprocess(course))


    def get_by_course_name(self, course_name):
        """按名称查询，没有周数要求，正常返回列表"""
        matched_courses = []
        for course in self.course_list:
            if re.search(course_name, course[0], re.IGNORECASE):
                matched_courses.append(course)

        return matched_courses

    def get_by_week_per(self, week_per, week_no=locate_week()):
        """按节次/周查询课程，返回匹配的课程列表。"""
        matched_courses0 = []
        matched_courses = []
        for course in self.course_list:
            if week_no in course[3]:
                matched_courses0.append(course)
        for course in matched_courses0:
            if course[1] == week_per:
                matched_courses.append(course)

        return matched_courses

    def get_by_week_no(self, week_no=locate_week()):
        """根据周次查询课程，返回在该周次有安排的课程列表。"""
        matched_courses = []
        for course in self.course_list:
            if week_no in course[3]:
                matched_courses.append(course)
        return matched_courses

    def get_by_teacher_name(self, teacher_name):
        """根据授课教师查询，返回在该周次有安排的课程列表。"""
        matched_courses = []
        for course in self.course_list:
            if re.search(teacher_name, course[5], re.IGNORECASE):
                matched_courses.append(course)
        return matched_courses

    def get_by_place_name(self, place):
        """根据周次查询课程，返回在该周次有安排的课程列表。"""
        matched_courses = []
        for course in self.course_list:
            if re.search(place, course[4], re.IGNORECASE):
                matched_courses.append(course)
        return matched_courses

    def get_by_date(self, date_str):
        """根据日期查询课程，返回在该日期有安排的课程列表。"""
        matched_courses = []  # 初始化存储匹配课程的列表
        week_no = locate_week(date_str)  # 使用locate_week确定周次
        date_obj = datetime.strptime(f"2024-{date_str}", "%Y-%m-%d")  # 假设年份为2024年
        week_day = '周' + ['一', '二', '三', '四', '五', '六', '日'][date_obj.weekday()]  # 确定星期几

        for course in self.course_list:
            if week_no in course[3] and course[1] == week_day:
                matched_courses.append(course)

        return matched_courses


    def preprocess(self, course_list):
        current_list = []
        current_list.append(course_list[0])
        current_list.append(course_list[1])
        current_list.append(course_list[2])
        current_list.append(self.process_weeks(course_list[3]))
        current_list.append(course_list[4])
        current_list.append(course_list[5])
        current_list.append(course_list[6])
        current_list.append(course_list[7])
        current_list.append(course_list[8])
        return current_list

    def process_weeks(self, text):
        if len(text[:-1]) < 3:
            return [int(text[:-1])]
        num_lst = text[:-1].split('-')
        a, b = int(num_lst[0]), int(num_lst[1])
        lst = list(range(a, b+1))

        return lst

    def print_course_list(self):
        for course in self.course_list:
            print(course)

    def locate_week(self):
        return locate_week()

    def download_new_pdf(self):
        # url = 'https://jw.njcit.cn/jwglxt/kbcx/xskbcx_cxXsShcPdf.html?doType=list'
        # response = requests.get(url, stream=True)
        #
        # # 检查请求是否成功
        # if response.status_code == 200:
        #     full_path = os.path.join('.', 'data', '课表.pdf')
        #     os.remove(os.path.join('.', 'data', '课表.pdf'))
        #
        #     with open(full_path, 'wb') as file:
        #         for chunk in response.iter_content(chunk_size=8192):
        #             if chunk:  # 过滤掉空的chunks
        #                 file.write(chunk)
        #     logger.success('读取新课表成功！')
        temp_list = []
        course_list = main()
        for course in course_list:
            temp_list.append(self.preprocess(course))
        self.course_list = temp_list
        del temp_list
        # else:
        #     logger.error('读取新课表失败！')

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

course = Course(get_new_course())
if __name__ == "__main__":
    print(locate_week())


