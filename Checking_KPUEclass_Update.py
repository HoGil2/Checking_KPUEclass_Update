from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import telegram
import os
import time

my_token = ''

bot = telegram.Bot(token = my_token)

chat_id = bot.getUpdates()[-1].message.chat.id

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

usr_id = ''
usr_pwd = '!'

def login():
    #로그인페이지
    login_page = 'http://eclass.kpu.ac.kr/ilos/main/member/login_form.acl'
    driver.get(login_page)
    ###
    if DEBUG == True:
        driver.get_screenshot_as_file('kpu_main.png')

    #로그인 아이디, 비밀번호 입력
    #####자동로그인하려면 암호화 필요
    while(login_page == driver.current_url):
        driver.find_element_by_name('usr_id').send_keys(usr_id)
        driver.find_element_by_name('usr_pwd').send_keys(usr_pwd)
        
        driver.find_element_by_xpath('//*[@id="login_btn"]').click()
        """
        try:
            alert = driver.switch_to_alert()
            alert.accept()
            print("아이디와 비밀번호를 확인해주세요.")
        except:
            continue
        """

    if DEBUG == True:
        driver.get_screenshot_as_file('kpu_main2.png')

def check_eclass_updates():
    subject = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#welcome_form > div > div > span.welcome_subject')))
    subtitles = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.submain-leftarea > div > div > div.title')))
    notices = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(\
            (By.CSS_SELECTOR, 'div.submain-leftarea > div > div.submain-noticebox > ol > li:nth-of-type(1) > em > a')))
    dates = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.submain-leftarea > div > div.submain-noticebox > ol > li:nth-child(1) > span')))
    latest_notices = []
    before_notices = []
    for i in range(len(subtitles)):
        latest_notices.append(subtitles[i].text+":"+notices[i].text+"\nDate:"+dates[i].text+"\n")
    try:
        with open(os.path.join(BASE_DIR, subject.text+'_latest_notices.txt'), 'r') as f_read:
            for k in range(len(subtitles)):
                before_notices.append(f_read.readline())
            f_read.close()
    except FileNotFoundError:
        with open(os.path.join(BASE_DIR, subject.text+'_latest_notices.txt'), 'w+') as f_write:
            for latest_notice in latest_notices:
                f_write.write(latest_notice)
            f_write.close()

    if before_notices != latest_notices:
        for latest_notice in latest_notices:  
            try:
                before_notices.index(latest_notice)
            except ValueError:
                print(latest_notice)
                bot.sendMessage(chat_id=chat_id, text=subject.text+' Updated >\n'+latest_notice)
        with open(os.path.join(BASE_DIR, subject.text+'_latest_notices.txt'), 'w+') as f_write:
            for latest_notice in latest_notices:
                f_write.write(latest_notice)
            f_write.close()

def open_first_eclass_room():
    try:
        eclass_room = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'sub_open')))
        eclass_room.click()
    except UnboundLocalError:
        print("개설된 eclass가 없습니다.")
        return False
    check_eclass_updates()
    return True

def open_others_eclass_room():
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//*[@id="subject-span"]'))).click()
    other_eclass_rooms = []
    try:
        other_eclass_rooms = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'roomGo')))
    except UnboundLocalError:
        return None

    eclass_rooms_jsf = []
    for eclass_room in other_eclass_rooms:
        eclass_rooms_jsf.append(eclass_room.get_attribute("onclick").strip())
    for eclass_room_jsf in eclass_rooms_jsf:
        driver.find_element(By.XPATH, '//*[@id="subject-span"]').click()
        driver.execute_script(eclass_room_jsf)
        check_eclass_updates()
        
if __name__=='__main__':
    start_time = time.time()

    login()
    
    if(open_first_eclass_room() != False):
        open_others_eclass_room()

    print("--- %s seconds ---" % (time.time() - start_time))
    driver.quit()