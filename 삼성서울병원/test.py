import os
import json
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"

def sanitize_filename(filename):
    """파일명에서 사용할 수 없는 문자를 제거하고 중복 파일명을 방지."""
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename

def check_url_status(url):
    """URL의 HTTP 상태 코드를 확인"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        print(f"HTTP Status Code: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"URL 확인 중 오류 발생: {e}")
        return False

def handle_alert(driver):
    """Alert 창이 뜰 경우 닫는 함수"""
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = Alert(driver)
        print(f"Alert Text: {alert.text}")
        alert.accept()
        print("Alert closed.")
    except:
        pass

def extract_sections(soup):
    """페이지 내의 섹션을 추출하여 JSON 구조로 반환"""
    data = {}

    # 질환명 추출
    disease_name_element = soup.select_one("h1.post-title strong")
    disease_name = disease_name_element.get_text(strip=True) if disease_name_element else "Unknown"
    data["질환명"] = disease_name

    # 관련진료과 추출
    department_element = soup.select_one("span.relation-data-detail")
    department = department_element.get_text(strip=True) if department_element else "정보 없음"
    data["관련진료과"] = department

    # 콘텐츠 섹션 추출
    sections = {
        "정의": "",
        "원인": "",
        "증상": "",
        "진단/검사": "",
        "치료": "",
        "경과/합병증": "",
        "예방/생활습관": "",
        "FAQ": ""
    }

    # 정의 섹션
    definition_element = soup.select_one("div.img")
    if definition_element:
        sections["정의"] = definition_element.get_text(separator="\n", strip=True)

    # 나머지 섹션들
    titles = soup.select("p.tit")
    contents = soup.select("div.cont")

    for title, content in zip(titles, contents):
        section_title = title.get_text(strip=True)
        section_content = content.get_text(separator="\n", strip=True)

        # 각 타이틀에 맞는 필드로 매핑
        if "원인" in section_title:
            sections["원인"] = section_content
        elif "증상" in section_title:
            sections["증상"] = section_content
        elif "진단" in section_title or "검사" in section_title:
            sections["진단/검사"] = section_content
        elif "치료" in section_title:
            sections["치료"] = section_content
        elif "경과" in section_title or "합병증" in section_title:
            sections["경과/합병증"] = section_content
        elif "예방" in section_title or "생활습관" in section_title:
            sections["예방/생활습관"] = section_content
        elif "FAQ" in section_title:
            sections["FAQ"] = section_content

    data["sections"] = sections
    return data

def crawl_page(url):
    """주어진 URL에서 데이터를 추출하여 JSON 파일로 저장"""
    if not check_url_status(url):
        print(f"URL 접근 불가 또는 잘못된 URL: {url}")
        return

    try:
        # WebDriver 설정
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        # Alert 창 닫기
        handle_alert(driver)

        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1.post-title"))
        )

        # 페이지 소스 추출
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        driver.quit()

        # 데이터 추출
        data = extract_sections(soup)

        # 파일명 생성
        filename = sanitize_filename(data["질환명"])
        file_path = os.path.join(RAW_DIR, f"{filename}.json")

        # 개별 파일 저장
        os.makedirs(RAW_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Data saved to {file_path}")

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

if __name__ == "__main__":
    test_url = input("Enter the URL to crawl: ").strip()
    crawl_page(test_url)