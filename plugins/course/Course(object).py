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

    def get_new_course_table(self):
        if download_pdf():
            temp_list = []
            course_list = main()
            for course in course_list:
                temp_list.append(self.preprocess(course))
            self.course_list = temp_list
            del temp_list
            logger.success('获取新课表成功！')
            return True
        else:
            logger.error('获取新课表失败！')
            return False