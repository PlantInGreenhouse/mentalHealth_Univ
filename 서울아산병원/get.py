import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

RAW_DIR = "data/raw"
BASE_URL = "https://www.amc.seoul.kr"
LIST_URL = "https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseList.do?pageIndex=1&partId=&diseaseKindId=C000006&searchKeyword=%EB%87%8C%EC%8B%A0%EA%B2%BD%EC%A0%95%EC%8B%A0%EC%A7%88%ED%99%98"
OUTPUT_FILE = os.path.join(RAW_DIR, "disease_links.json")

def get_disease_links(driver):
    """현재 페이지에서 질병명에 해당하는 링크들만 추출하여 리스트로 반환"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    disease_links = []

    # 질병명에 해당하는 링크들 추출
    list_items = soup.select("ul.descBox li .contBox strong.contTitle a")
    for item in list_items:
        href = item.get("href")
        if href and "diseaseDetail.do?contentId=" in href:
            full_url = BASE_URL + href
            disease_links.append(full_url)

    return disease_links

def save_links_to_json(links):
    """모든 링크를 하나의 JSON 파일에 저장"""
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

def navigate_pages(driver):
    """모든 페이지를 순회하며 링크를 수집"""
    all_links = []

    for page_num in range(1, 9):
        print(f"Processing page {page_num}...")
        
        # 현재 페이지의 링크 추출
        links = get_disease_links(driver)
        all_links.extend(links)

        # 다음 페이지로 이동 (onclick 이벤트 트리거)
        try:
            next_page = driver.find_element(By.XPATH, f"//a[@onclick='fnList({page_num + 1}); return false;']")
            driver.execute_script("arguments[0].click();", next_page)
            time.sleep(2)  # 페이지 로딩 대기
        except Exception as e:
            print(f"Error navigating to page {page_num + 1}: {e}")
            break

    # 저장
    save_links_to_json(all_links)

def collect_disease_links():
    """크롤링 시작"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(LIST_URL)
        time.sleep(2)  # 페이지 로딩 대기

        navigate_pages(driver)

    except Exception as e:
        print(f"Error during link collection: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    collect_disease_links()