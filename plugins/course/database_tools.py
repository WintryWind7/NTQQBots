import sqlite3
import os
from nonebot import logger

def current_path(*args):
    """用于获取准确的目录"""
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(current_script_path, *args)
    return data_file_path


def drop_datebase(db_name=current_path('data', 'course.db')):
    conn = sqlite3.connect(db_name)  # 请替换 'your_database.db' 为你的数据库名
    cursor = conn.cursor()
    try:
        # 删除名为todays_course的表
        cursor.execute("DROP TABLE todays_course")
        print("表todays_course已成功删除。")

        # 提交事务（尽管DROP TABLE是一个自动提交的操作，但这里保持一致性）
        conn.commit()
    except sqlite3.Error as e:
        print(f"删除表时出错: {e}")
    finally:
        # 关闭游标
        cursor.close()
        # 关闭数据库连接
        conn.close()

def create_database(db_name=current_path('data', 'course.db')):
    """创建一个表"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 创建一个表（仅当表不存在时）
    cursor.execute('''  
CREATE TABLE IF NOT EXISTS todays_course (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    course_name TEXT NOT NULL,  
    period_per_week TEXT NOT NULL,  
    period_per_day TEXT NOT NULL,  
    week_no TEXT NOT NULL,  
    place TEXT NOT NULL,  
    teacher TEXT NOT NULL,  
    class_composition TEXT NOT NULL,  
    credits TEXT NOT NULL,  
    specific_time TEXT NOT NULL  
)  
'''  )

    conn.commit()
    conn.close()


def reset_and_insert_today_course(data_list, db_name=current_path('data', 'course.db'), ):
    """
    先清空todays_course表，然后插入新的课程数据。

    :param db_connection: 数据库连接对象
    :param data_list: 包含课程数据的列表，每个元素是一个元组，对应表中的一行记录
    """
    db_connection = sqlite3.connect(db_name)
    cursor = db_connection.cursor()

    # try:
    # 清空todays_course表
    cursor.execute(f"DELETE FROM todays_course")

    # 使用executemany()方法批量插入数据
    cursor.executemany('''  
        INSERT INTO todays_course (course_name, period_per_week, period_per_day, week_no, place, teacher, class_composition, credits, specific_time)  
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)  
    ''', data_list)
    db_connection.commit()
    # except sqlite3.Error as e:
    #     logger.error("操作数据库时出错: {e}")
    #     db_connection.rollback()  # 回滚事务
    # finally:
    #     cursor.close()  # 关闭游标


def get_db_todays_course_row():
    db_path = current_path('data', 'course.db')
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM todays_course ORDER BY id LIMIT 1")
        result = cur.fetchone()
        if result:
            return list(result)  # 将结果转换为列表并返回
        else:
            return None  # 如果没有数据，返回None
    finally:
        # 关闭数据库连接
        conn.close()

def del_db_todays_course_row():
    db_path = current_path('data', 'course.db')
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM todays_course WHERE id IN (SELECT id FROM todays_course ORDER BY id LIMIT 1)")
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    print(get_db_todays_course_row())