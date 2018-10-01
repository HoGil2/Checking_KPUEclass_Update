from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Pool
import os
import time

DEBUG = False
options = webdriver.ChromeOptions()
#headless이게하는 코드
"""
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
"""
#headless가 아닌척 하기
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36

#파일생성 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
driver = webdriver.Chrome('C:/Users/rlf03/Downloads/chromedriver_win32/chromedriver.exe', chrome_options=options)

#headless가 아닌척 하기
#user_agent = driver.find_element_by_css_selector('#user-agent')
#print('User-Agent: ', user_agent)

def login():
    #로그인페이지
    login_page = 'http://eclass.kpu.ac.kr/ilos/main/member/login_form.acl'
    driver.get(login_page)
    ###
    if DEBUG == True:
        driver.get_screenshot_as_file('kpu_main.png')

    #로그인 아이디, 비밀번호 입력
    #####자동로그인하려면 암호화 필요
    
    usr_id = input("아이디를 입력해주세요.")
    usr_pwd = input("비밀번호를 입력해주세요.")
    driver.find_element_by_name('usr_id').send_keys(usr_id)
    driver.find_element_by_name('usr_pwd').send_keys(usr_pwd)
    
    #####로그인 상태 체크해야됨
    #driver.find_element_by_name('myform').submit
    driver.find_element_by_xpath('//*[@id="login_btn"]').click()
    ###
    if DEBUG == True:
        driver.get_screenshot_as_file('kpu_main2.png')

def check_eclass_updates(room_code):
    driver.execute_script(room_code)
    subject = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#welcome_form > div > div > span.welcome_subject')))
    subtitles = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.submain-leftarea > div > div > div.title')))
    notices = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(\
            (By.CSS_SELECTOR, 'div.submain-leftarea > div > div.submain-noticebox > ol > li:nth-of-type(1) > em > a')))
    latest_notices = []
    before_notices = []
    for i in range(len(subtitles)):
        latest_notices.append(subtitles[i].text + ":" + notices[i].text + "\n")
    try:
        with open(os.path.join(BASE_DIR, subject.text+'_latest_notices.txt'), 'r') as f_read:
            for k in range(len(subtitles)):
                before_notices.append(f_read.readline())
            f_read.close()
    except FileNotFoundError:
        with open(os.path.join(BASE_DIR, subject.text+'_latest_notices.txt'), 'w+') as f_write:
            for k in range(len(latest_notices)):
                f_write.write(latest_notices[k])
            f_write.close()

    if before_notices != latest_notices:
        for k in range(len(latest_notices)):
            ln = latest_notices[k]
            ###
            if DEBUG == True:
                print(ln)
            ###
            try:
                before_notices.index(ln)
            except ValueError:
                #새글이 올라왔으면 need_to_rewrite==True
                need_to_rewrite = True
                #bot.sendMessage(chat_id=chat_id, text='새 글이 올라왔어요!')
                print("updated > "+ln)
        with open(os.path.join(BASE_DIR, subject.text+'_latest_notices.txt'), 'w+') as f_write:
            for k in range(len(latest_notices)):
                f_write.write(ln)
            f_write.close()

def open_eclass_room(room_code):
    home = 'http://eclass.kpu.ac.kr/ilos/main/main_form.acl'
    driver.get(home)
    driver.set_page_load_timeout(30)
    for handle in driver.window_handles:
        driver.switch_to_window(handle)
        check_eclass_updates(room_code)

if __name__=='__main__':
    start_time = time.time()

    login()
    
    #eclass 개설된 강좌 수
    MAX_SUB = len(driver.find_elements(By.CLASS_NAME,'sub_open'))
    eclass_rooms = driver.find_elements(By.CLASS_NAME,'sub_open')
    eclass_room_jsf = []
    for eclass_room in eclass_rooms:
        eclass_room_jsf.append(eclass_room.get_attribute("onclick").strip())
    #open_eclass_room(eclass_room_jsf[0])
    pool = Pool(processes = MAX_SUB)
    pool.map(open_eclass_room, eclass_room_jsf)

    print("--- %s seconds ---" % (time.time() - start_time))
    driver.quit()