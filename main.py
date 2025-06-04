from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import time
from enum import Enum, auto
from datetime import datetime, timedelta
import json

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

config = load_config('config.json')
class Constants(Enum):
    ID = config["USER_ID"]
    PW = config["USER_PW"]

    LOGIN_URL = config["LOGIN_URL"]
    RESERVATION_URL = config["RESERVATION_URL"]

    TIMEOUT: float = 6000

# Chrome 브라우저의 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# 창을 전체화면으로 설정
driver.maximize_window()

stadium = ""

# 10시까지 대기하는 함수
def wait_until():
    now = datetime.now()
    # 오늘의 10:00 AM 설정
    target_time = now.replace(hour=10, minute=0, second=0, microsecond=300000)

    # 현재 시간이 10:00 AM 이후인 경우, 다음 날 10:00 AM으로 설정
    if now > target_time:
        target_time += timedelta(days=1)

    now = datetime.now()
    if now < target_time:
        wait_time = (target_time - now).total_seconds()
        print(f"{wait_time}초 동안 대기합니다. 목표 시간: {target_time.strftime('%H:%M:%S')}")
        time.sleep(wait_time)
    else:
        print("목표 시간이 이미 지나버렸습니다.")

# 예약 옵션 가져오기
def get_selected_option():
    global stadium  # 전역 변수를 사용
    driver.get("file:///Users/incross0915/Desktop/PrivateProject/Private/ReservationMacro/index.html")  

    while True:
        selected_option = driver.execute_script("return localStorage.getItem('reservation_option');")
        if selected_option:
            print(f"선택된 옵션: {selected_option}")
            stadium = selected_option
            return selected_option
        else:
            print("옵션이 선택되지 않았습니다. 다시 확인합니다...")
            time.sleep(2)  # 2초마다 확인

# 로그인 함수
def login():
    # 페이지 열기
    driver.get(Constants.LOGIN_URL.value)

    # 페이지 로딩을 기다리기
    WebDriverWait(driver, Constants.TIMEOUT.value).until(EC.presence_of_element_located((By.ID, "user_id")))

    # 사용자 아이디 입력 필드 찾기
    user_id_field = driver.find_element(By.ID, "user_id")
    user_id_field.clear()  # 기존 값 지우기 (선택 사항)
    user_id_field.send_keys(Constants.ID.value)  # 아이디 입력하기

    # 비밀번호 입력 필드 찾기
    password_field = driver.find_element(By.ID, "user_password")
    password_field.clear()  # 기존 값 지우기 (선택 사항)
    password_field.send_keys(Constants.PW.value)  # 비밀번호 입력하기

    # 로그인 버튼 클릭하기
    login_button = WebDriverWait(driver, Constants.TIMEOUT.value).until(
        EC.element_to_be_clickable((By.XPATH, '//button[text()="로그인"]'))
    )
    login_button.click()

def ready_for_reservation() :
    global stadium  # 전역 변수 stadium을 사용

    time.sleep(3)

    # 페이지 열기
    driver.get(Constants.RESERVATION_URL.value)

    # '오늘 하루 안보기' 버튼 찾기 (XPATH로 찾기)
    # today_button = WebDriverWait(driver, Constants.TIMEOUT.value).until(
    #     EC.element_to_be_clickable((By.XPATH, '//button[span[text()="오늘 하루 안보기"]]')))
    # today_button.click()

    # select 요소 찾기
    select_element = WebDriverWait(driver, Constants.TIMEOUT.value).until(EC.presence_of_element_located((By.ID, "center")))
    select = Select(select_element)

    if stadium == "시민체육광장":
        select.select_by_value("GUNPO02")  # value 속성을 사용하여 선택
    else:
        select.select_by_value("GUNPO01")  # value 속성을 사용하여 선택

        time.sleep(3)

        # '시설' select 요소 찾기
        part_select_element = WebDriverWait(driver, Constants.TIMEOUT.value).until(EC.presence_of_element_located((By.ID, "part")))
        part_select = Select(part_select_element)

        # '축구장'을 선택 (value="11")
        part_select.select_by_value("11")

    time.sleep(2)

    # 조회 버튼 찾기 (CSS 선택자로 찾기)
    submit_button = WebDriverWait(driver, Constants.TIMEOUT.value).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.submit[type="submit"]')))

    # submit_button이 제대로 찾았는지 확인
    if submit_button:
        print("Submit button found:")
        print(f"Button text: {submit_button.text}")
        print(f"Button class: {submit_button.get_attribute('class')}")
    else:
        print("Submit button not found")

    # 조회 버튼 클릭하기
    submit_button.click()

    time.sleep(2)  # 페이지 로딩을 기다리기

    # '다음월' 링크 클릭하기
    next_month_link = wait_for_clickable(driver, By.ID, "next_month")
    next_month_link.click()

    time.sleep(2)

    # 특정 날짜(td) 클릭하기 ex) 당일이 8/2일 이면 9/2일을 선택
    # 혹시 모를 일로 인하여 부득이하게 하드코딩으로 진행
    date_td = WebDriverWait(driver, Constants.TIMEOUT.value).until(
        EC.element_to_be_clickable((By.ID, "date-20250704"))
    )
    date_td.click()

    wait_until()  # 10:00 AM까지 대기

    # 08:00 ~ 10:00 체크박스 선택
    while True:
        driver.refresh()  # 페이지 새로고침
        try:
            checkbox = WebDriverWait(driver, 0.5).until(
                EC.element_to_be_clickable((By.ID, "checkbox_time_1"))
            )
            checkbox.click()
            print("Checkbox clicked successfully!")
            break  # 체크박스가 발견되면 루프 종료
        except:
            print("Checkbox not found, refreshing the page...")

def wait_for_clickable(driver, by, value, timeout=10, retries=3):
    for _ in range(retries):
        try:
            return WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
        except StaleElementReferenceException:
            time.sleep(1)  # 1초 대기 후 다시 시도
    raise Exception("Element not found or stale after retries.")

def apply_for_reservation():
    # 페이지 로딩을 기다리기
    WebDriverWait(driver, Constants.TIMEOUT.value).until(EC.presence_of_element_located((By.ID, "team_nm")))

    # 삼성 마을 구장 전용
    # '팀명' 입력 필드 찾기 및 값 입력 
    if stadium == "군포국민체육센터":
        team_nm_field = driver.find_element(By.ID, "team_nm")
        team_nm_field.clear()  # 기존 값 지우기 (선택 사항)
        team_nm_field.send_keys("김민제")  # 팀명 입력하기

    # '인원수' 입력 필드 찾기 및 값 입력
    users_field = driver.find_element(By.ID, "users")
    users_field.clear()  # 기존 값 지우기 (선택 사항)
    users_field.send_keys("14명")  # 인원수 입력하기

    # '목적' 입력 필드 찾기 및 값 입력
    purpose_field = driver.find_element(By.ID, "purpose")
    purpose_field.clear()  # 기존 값 지우기 (선택 사항)
    purpose_field.send_keys("축구")  # 목적 입력하기

    # 페이지 로딩을 기다리기
    WebDriverWait(driver, Constants.TIMEOUT.value).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # JavaScript를 사용하여 스크롤을 페이지 맨 아래로 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # 페이지 로딩을 기다리기
    WebDriverWait(driver, Constants.TIMEOUT.value).until(EC.presence_of_element_located((By.ID, "agree_use1")))

    # 체크박스 요소 찾기
    checkbox = driver.find_element(By.ID, "agree_use1")

    # 체크박스가 이미 체크되어 있지 않다면 클릭하여 체크
    if not checkbox.is_selected():
        checkbox.click()

# try:
#     get_selected_option()
#     login()
#     ready_for_reservation()
#     apply_for_reservation()

#     # 무한 루프를 사용하여 대기
#     while True:
#         time.sleep(1)  # 1초마다 반복 (CPU 사용을 줄이기 위해)
# finally:
#     # 드라이버 종료
#     driver.quit()

selected_option = get_selected_option()
if selected_option:
    login()
    ready_for_reservation()
    apply_for_reservation()

    # 무한 루프를 사용하여 대기
    while True:
        time.sleep(1)  # 1초마다 반복 (CPU 사용을 줄이기 위해)
else:
    print("예약 옵션이 설정되지 않아 프로그램을 종료합니다.")
    driver.quit()