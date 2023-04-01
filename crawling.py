import xml.etree.ElementTree as elemTree
from selenium import webdriver
from bs4 import BeautifulSoup
import keyboard, time
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.background import BlockingScheduler

# pip install apscheduler

class Lecture:
    def __init__(self):
        self.index = None
        self.title = None
        self.period = None
        self.date = None
        self.number = None
        self.mentor = None

def Crawling():
    print("Crawling 시작")
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('chromedriver', options=options)
    driver.get('https://www.swmaestro.org/sw/member/user/forLogin.do?menuNo=200025')
    time.sleep(1)

    tree = elemTree.parse('keys.xml')
    loginID = tree.find('string[@name="somaID"]').text
    loginPW = tree.find('string[@name="somaPW"]').text
    driver.find_element(By.XPATH, '//*[@id="username"]').click()
    time.sleep(1)
    keyboard.write(loginID)
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="password"]').click()
    time.sleep(1)
    keyboard.write(loginPW)
    time.sleep(1)
    # Login
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div/div[1]/div/dl/dd/button').click()
    time.sleep(1)
    # MyPage
    driver.find_element(By.XPATH, '/html/body/header/div/a[2]').click()
    time.sleep(1)
    # Mentoring
    driver.find_element(By.XPATH, '//*[@id="contentsList"]/div/div/ul/li[4]/a').click()
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lectures = soup.find("table", attrs={"class":"tbl-st1 t"}).find_all("tr")
    last_index = -1
    first_index = None
    print_lecture = []
    try:
        with open('data/index.txt', 'r', encoding='utf-8') as f:
            last_index = int(f.read())
    except: pass
    for lecture in lectures[1:]:
        index, title, period, date, number, _, mentor, _ = lecture.find_all("td")
        index = int(index.get_text().strip())
        if last_index >= index: break
        if first_index is None: first_index = index
        lectData = Lecture()
        lectData.index = index
        lectData.title = title.find("a").get_text().replace("\n", "").strip()
        lectData.period = period.find("a").get_text().replace("\n", "").replace("\t", "").strip()
        lectData.date = date.get_text().replace("\n", "").replace("\t", "").strip()
        lectData.number = number.get_text().replace("\n", "").replace("\t", "").strip().split("/")[1]
        lectData.mentor = mentor.get_text().strip()
        print_lecture.append(lectData)

    driver.close()

    # 마지막 인덱스 기억하기
    if first_index is not None:
        with open('data/index.txt', 'w', encoding='utf-8') as f:
            f.write(str(first_index))
    
    with open('data/crawling.txt', 'w', encoding='utf-8') as f:
        for lecture in print_lecture:
            f.write(f"{lecture.title}＃{lecture.period}＃{lecture.date}＃{lecture.number}＃{lecture.mentor}\n")
    
    print("Crawling 종료")

# Crawling()
scheduler = BlockingScheduler(timezone='Asia/Seoul')
scheduler.add_job(Crawling, 'interval', seconds=30, id='crawling')
scheduler.start()