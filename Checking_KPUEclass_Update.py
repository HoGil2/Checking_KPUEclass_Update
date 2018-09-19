from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
import sys
from timeit import default_timer as timer

DEBUG = False
start = timer()

options = webdriver.ChromeOptions()
#headless이게하는 코드
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

#파일생성 위치
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#headless가 아닌척 하기
#options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36

driver = webdriver.Chrome('C:/Users/rlf03/Downloads/chromedriver_win32/chromedriver.exe', chrome_options=options)

#로그인페이지
driver.get('http://eclass.kpu.ac.kr/ilos/main/member/login_form.acl')
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

#headless가 아닌척 하기
#user_agent = driver.find_element_by_css_selector('#user-agent')
#print('User-Agent: ', user_agent)

#eclass 개설된 강좌 수
MAX_SUB = 20
home = 'http://eclass.kpu.ac.kr/ilos/main/main_form.acl'

for i in range(1, MAX_SUB+1):
    driver.get(home)
    ###
    if DEBUG == True:
        driver.get_screenshot_as_file('home.png')
    ###
    subjects_path = '//*[@id="contentsIndex"]/div[2]/div[2]/ol/li['+str(i)+']/em'
    #####개선필요 클릭할때 없는 강좌인지 확인가능하면 속도향상
    driver.find_element_by_xpath(subjects_path).click()
    ###
    if DEBUG == True:
        driver.get_screenshot_as_file('kpu_subject'+str(i)+'.png')
    ###
    try:
        lxml = driver.page_source
    except:
        end = timer()
        print(end - start)
        driver.quit()
        break
    soup = BeautifulSoup(lxml, "lxml")
    latest_notices = []
    before_notices = []
    subjects = soup.select('#welcome_form > div.welcome_title.site-mouseover-color > div > span.welcome_subject')
    #현재 개설된 타이틀만 오픈
    subtitles = soup.select('div.submain-leftarea > div > div > div.title')
    notices = soup.select('div.submain-leftarea > div > div.submain-noticebox > ol > li:nth-of-type(1) > em > a')
    for j in range(len(subtitles)):
        ###
        if DEBUG == True:
            print(subtitles[j].text)
            print(notices[j].text)
        ###
        latest_notices.append(subtitles[j].text + ":" + notices[j].text +"\n")
    name_subject = subjects[0].text
    try:
        with open(os.path.join(BASE_DIR, name_subject+'_latest_notices.txt'), 'r') as f_read:
            for k in range(len(subtitles)):
                before_notices.append(f_read.readline())
            f_read.close()
    except FileNotFoundError:
        with open(os.path.join(BASE_DIR, name_subject+'_latest_notices.txt'), 'w+') as f_write:
            for k in range(len(latest_notices)):
                f_write.write(latest_notices[k])
            f_write.close()
            continue

    need_to_rewrite = False
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
    if need_to_rewrite == True:
        with open(os.path.join(BASE_DIR, name_subject+'_latest_notices.txt'), 'w+') as f_write:
            for k in range(len(latest_notices)):
                f_write.write(ln)
            f_write.close()

driver.quit()