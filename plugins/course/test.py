import time
from selenium import webdriver
import os
import shutil
from get_course import current_path

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
    time.sleep(10)
    path = r'C:\Users\Win\Downloads'
    file = [file for file in os.listdir(path) if file.endswith('.pdf')][0]
    time.sleep(180)
    if os.path.exists(os.path.join(path, file)):
        shutil.move(os.path.join(path, file), current_path('data', 'course.pdf'))

if __name__ == "__main__":
    download_pdf()