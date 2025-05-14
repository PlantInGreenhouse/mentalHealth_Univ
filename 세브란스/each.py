import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

OUTPUT_DIR = "data/disease_data"
BASE_URL = "https://sev.severance.healthcare"
TARGET_URL = "https://sev.severance.healthcare/health/encyclopedia/disease/system.do?&mode=view&articleNo=69768&srDiseaseCategoryId=275&articleLimit=0"

def parse_content(soup):
    """ 콘텐츠를 JSON 형식으로 파싱 """
    data = {}
    sections = {}
    images = []
    tags = []

    # 질병명 및 영문명 추출
    title_tag = soup.select_one("div.article-header h3.subject")
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        if "[" in title_text and "]" in title_text:
            disease_name, eng_name = title_text.split("[")
            data["질병명"] = disease_name.strip()
            data["영문명"] = eng_name.replace("]", "").strip()
        else:
            data["질병명"] = title_text.strip()
            data["영문명"] = ""

    # 본문 내용 추출
    content_divs = soup.select("div.article-body .fr-view")
    current_section = None
    section_content = []

    for content_div in content_divs:
        for element in content_div.find_all(["ul", "p", "img"]):
            if element.name == "ul":
                for li in element.find_all("li"):
                    # 기존 섹션 저장
                    if current_section and section_content:
                        sections[current_section] = "\n".join(section_content).strip()

                    # 새로운 섹션 시작
                    current_section = li.get_text(strip=True)
                    section_content = []

            elif element.name == "p":
                content_text = element.get_text(separator="\n").strip()
                if content_text:
                    section_content.append(content_text)

            elif element.name == "img":
                img_src = element.get("src")
                if img_src and img_src not in images:
                    images.append(img_src)

    # 마지막 섹션 저장
    if current_section and section_content:
        sections[current_section] = "\n".join(section_content).strip()

    data["sections"] = sections
    data["images"] = images

    # TAG 정보 추출
    tag_elements = soup.select("div.tag-wrap dl dd a")
    for tag in tag_elements:
        tags.append(tag.get_text(strip=True))
    data["tags"] = tags

    return data

def save_to_json(data, file_name):
    """ JSON 파일로 저장 """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"{file_name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def process_page(driver, url):
    """ 페이지에서 데이터를 추출하고 저장 """
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

def main():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        process_page(driver, TARGET_URL)

    except Exception as e:
        print(f"Error in main function: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()