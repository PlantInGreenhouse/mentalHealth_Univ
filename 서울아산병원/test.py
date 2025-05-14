import os
import json
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

RAW_DIR = "data/raw"
LINKS_FILE = "data/raw/disease_links.json"
OUTPUT_ALL_FILE = os.path.join(RAW_DIR, "disease_data_all.json")

def sanitize_filename(filename):
    """파일명에서 사용할 수 없는 문자를 제거하고 중복 파일명을 방지."""
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    counter = 1
    original_filename = filename

    while os.path.exists(os.path.join(RAW_DIR, f"{filename}.json")):
        filename = f"{original_filename}_{counter}"
        counter += 1

    return filename

def extract_sections(soup):
    """페이지 내의 섹션을 추출하여 JSON 구조로 반환"""
    data = {
        "title": "",
        "symptoms": [],
        "related_diseases": [],
        "departments": [],
        "synonyms": [],
        "sections": {}
    }

    # 질환명 추출
    title_element = soup.select_one("div.contBox > strong.contTitle")
    if title_element:
        data["title"] = title_element.get_text(strip=True)

    # 증상 추출
    symptom_elements = soup.select("dt:contains('증상') + dd a")
    if symptom_elements:
        data["symptoms"] = [symptom.get_text(strip=True) for symptom in symptom_elements]

    # 관련질환 추출
    related_diseases_elements = soup.select("dt:contains('관련질환') + dd a")
    if related_diseases_elements:
        data["related_diseases"] = [disease.get_text(strip=True) for disease in related_diseases_elements]

    # 진료과 추출
    departments_elements = soup.select("dt:contains('진료과') + dd a")
    if departments_elements:
        data["departments"] = [dept.get_text(strip=True) for dept in departments_elements]

    # 동의어 추출
    synonym_element = soup.select_one("dt:contains('동의어') + dd")
    if synonym_element:
        synonyms = synonym_element.get_text(separator=",", strip=True).split(",")
        data["synonyms"] = [syn.strip() for syn in synonyms]

    # 메인 섹션 추출
    main_sections = {}
    main_section_elements = soup.select("div.contDescription dl.descDl dt")

    for section in main_section_elements:
        section_title = section.get_text(strip=True)
        section_content = section.find_next_sibling("dd").get_text(separator="\n", strip=True)
        main_sections[section_title] = section_content

    data["sections"]["메인 섹션"] = main_sections

    return data

def handle_alert(driver):
    """경고창을 닫는 함수"""
    try:
        alert = Alert(driver)
        alert.accept()
        print("Alert closed.")
    except:
        pass

def crawl_page(url):
    """주어진 URL에서 데이터를 추출하여 JSON 파일로 저장"""
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        time.sleep(2)

        handle_alert(driver)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        driver.quit()

        data = extract_sections(soup)

        # 파일명 생성
        filename = sanitize_filename(data["title"])
        file_path = os.path.join(RAW_DIR, f"{filename}.json")

        # 개별 파일 저장
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Data saved to {file_path}")

        return data

    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        return None

def process_all_links():
    """disease_links.json에 있는 모든 URL을 순회하며 데이터를 추출"""
    if not os.path.exists(LINKS_FILE):
        print(f"{LINKS_FILE} 파일이 존재하지 않습니다.")
        return

    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        urls = json.load(f)

    print(f"총 {len(urls)}개의 URL이 발견되었습니다.")

    all_data = []

    for url in urls:
        print(f"Processing: {url}")
        data = crawl_page(url)
        if data:
            all_data.append(data)
        time.sleep(1)

    with open(OUTPUT_ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"All data saved to {OUTPUT_ALL_FILE}")

if __name__ == "__main__":
    process_all_links()