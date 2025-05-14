import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
OUTPUT_DIR = "data/disease_data"
LINKS_FILE = os.path.join(RAW_DIR, "disease_links.json")

def parse_content(soup):
    """ 콘텐츠를 JSON 형식으로 파싱 """
    data = {}
    sections = {}

    # 질병명 및 영문명 추출
    title_tag = soup.select_one("div.article-header h3.subject")
    if title_tag:
        title_text = title_tag.text.strip()
        if "[" in title_text and "]" in title_text:
            disease_name, eng_name = title_text.split("[")
            data["질병명"] = disease_name.strip()
            data["영문명"] = eng_name.replace("]", "").strip()
        else:
            data["질병명"] = title_text.strip()
            data["영문명"] = ""

    # 콘텐츠 추출
    content_div = soup.select_one("div.article-body .fr-view")
    if content_div:
        current_section = None
        section_content = []

        for element in content_div.find_all(["li", "p"]):
            if element.name == "li":
                # 이전 섹션 저장
                if current_section and section_content:
                    sections[current_section] = "\n".join(section_content).strip()
                
                # 새로운 섹션 시작
                current_section = element.get_text(strip=True)
                section_content = []

            elif element.name == "p" and current_section:
                # 섹션 내용에 추가
                content_text = element.get_text(separator="\n").strip()
                if content_text:
                    section_content.append(content_text)

        # 마지막 섹션 저장
        if current_section and section_content:
            sections[current_section] = "\n".join(section_content).strip()

    data["sections"] = sections

    return data

def save_to_json(data, file_name):
    """ JSON 파일로 저장 """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"{file_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_disease_page(driver, url):
    """ 각 질병 페이지에서 데이터를 추출하고 저장 """
    try:
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기
        soup = BeautifulSoup(driver.page_source, "html.parser")
        data = parse_content(soup)

        # 파일명은 질병명으로 저장
        file_name = data.get("질병명", "unknown").replace(" ", "_")
        save_to_json(data, file_name)

        print(f"Data saved for {file_name}")

    except Exception as e:
        print(f"Error processing {url}: {e}")

def collect_data_from_links():
    """ 저장된 링크들을 순회하며 데이터를 수집 """
    if not os.path.exists(LINKS_FILE):
        print(f"Links file not found: {LINKS_FILE}")
        return

    # 링크 로드
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        links = json.load(f)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        for link in links:
            print(f"Processing {link}")
            process_disease_page(driver, link)

    except Exception as e:
        print(f"Error during data collection: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    collect_data_from_links()