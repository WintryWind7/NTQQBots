import time
from selenium import webdriver
import os
import shutil
from datetime import datetime

def current_path(*args):
    """用于获取准确的目录"""
    current_script_path = os.path.dirname(os.path.abspath(__file__))
    data_file_path = os.path.join(current_script_path, *args)
    return data_file_path
def download_pdf():
    driver = webdriver.Edge()
    driver.get('https://jw.njcit.cn/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N2151&layout=default')
    # time.sleep(2)
    driver.find_element('xpath', '/html/body/div[1]/div[2]/div[2]/form/div/div/div[1]/div[1]/div/input').send_keys('220402117')
    driver.find_element('xpath', '/html/body/div[1]/div[2]/div[2]/form/div/div/div[1]/div[2]/div/input[2]').send_keys('2272Wintry!')
    driver.find_element('xpath', '/html/body/div[1]/div[2]/div[2]/form/div/div/div[1]/div[3]/button').click()
    time.sleep(1)
    driver.find_element('xpath', '/html/body/div[2]/div/div/form/div/div[3]/div/div/button').click()
    driver.find_element('xpath', "/html/body/div[2]/div/div/div[1]/div/div[2]/button[3]").click()
    time.sleep(3)
    driver.find_element('xpath', '/html/body/div[2]/div/div/div[1]/div/div[2]/button[1]').click()   # 下载
    time.sleep(15)
    path = r'C:\Users\Win\Downloads'
    file = [file for file in os.listdir(path) if file.endswith('.pdf')][0]
    time.sleep(1)
    if os.path.exists(os.path.join(path, file)):
        remove_file = [file for file in os.listdir(current_path('data')) if file.endswith('.pdf')][0]
        os.remove(current_path('data', remove_file))
        time.sleep(1)
        file_name = 'course' + datetime.today().strftime('%m%d') + '.pdf'
        shutil.move(os.path.join(path, file), current_path('data', file_name))
        return True
    else:
        return None

if __name__ == "__main__":
    download_pdf()