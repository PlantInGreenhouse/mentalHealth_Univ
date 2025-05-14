import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urljoin

RAW_DIR = "data/raw"
LIST_URL = "https://sev.severance.healthcare/health/encyclopedia/disease/system.do?mode=list&srSearchKey=&empNo=&seq=&srBodyCategoryId=&srDiseaseCategoryId=275&srSearchVal="
OUTPUT_FILE = os.path.join(RAW_DIR, "disease_links.json")
BASE_URL = "https://sev.severance.healthcare/health/encyclopedia/disease/system.do"

def get_disease_links(driver):
    """질병명에 해당하는 링크들을 추출하여 리스트로 반환"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    disease_links = []

    # .thumb-list.type2 내부의 .thumb-item 내 a 태그에서 href 추출
    items = soup.select("div.thumb-list.type2 div.thumb-item a.inner")
    
    for item in items:
        href = item.get("href")
        if href:
            # 쿼리 파라미터 추출
            params = parse_qs(href.lstrip("?"))
            article_no = params.get("articleNo", [""])[0]
            sr_disease_category_id = params.get("srDiseaseCategoryId", [""])[0]

            # 필수 파라미터가 존재하는 경우에만 링크 생성
            if article_no and sr_disease_category_id:
                # 최종 링크 생성
                full_url = (
                    f"{BASE_URL}?&mode=view&articleNo={article_no}"
                    f"&srDiseaseCategoryId={sr_disease_category_id}&articleLimit=0"
                )
                disease_links.append(full_url)

    return disease_links

def save_links_to_json(links):
    """링크들을 JSON 파일에 저장"""
    os.makedirs(RAW_DIR, exist_ok=True)

    # 기존 파일이 있다면 불러오기
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_links = json.load(f)
    else:
        existing_links = []

    # 중복 제거 후 병합
    combined_links = list(set(existing_links + links))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(combined_links, f, ensure_ascii=False, indent=4)

    print(f"Total {len(combined_links)} unique links saved to {OUTPUT_FILE}")

def collect_disease_links():
    """크롤링 시작 - 다중 페이지를 순회하며 링크 추출"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        offset = 0
        all_links = []

        while True:
            # 페이지 URL 생성
            page_url = f"{LIST_URL}&article.offset={offset}&articleLimit=12"
            print(f"Processing page with offset {offset}...")

            # 페이지 로드
            driver.get(page_url)
            time.sleep(2)  # 페이지 로딩 대기

            # 링크 추출
            links = get_disease_links(driver)

            # 만약 더 이상 링크가 없다면 종료
            if not links:
                print("No more links found. Stopping...")
                break

            # 수집된 링크들을 추가
            all_links.extend(links)

            # offset 증가 (12개씩)
            offset += 12

        # 최종 저장
        save_links_to_json(all_links)

    except Exception as e:
        print(f"Error during link collection: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    collect_disease_links()