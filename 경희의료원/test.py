import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# JSON 파일 경로
json_path = "data/khmc_links.json"
output_dir = "data/raw"

# 출력 디렉터리가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# Chrome 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 백그라운드에서 실행
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# JSON 파일 읽기
with open(json_path, "r", encoding="utf-8") as file:
    links_data = json.load(file)

# URL 리스트 순회
for url in links_data:
    if not isinstance(url, str):
        print(f"Invalid entry: {url}")
        continue

    try:
        driver.get(url)
        time.sleep(2)  # 페이지 로딩 대기

        # 제목
        try:
            title_element = driver.find_element(By.CSS_SELECTOR, "p.title#title")
            title = title_element.text.strip()
        except:
            title = "제목 없음"

        # 출처
        try:
            dept_element = driver.find_element(By.CSS_SELECTOR, "label#deptNm")
            department = dept_element.text.strip()
        except:
            department = "출처 없음"

        # 본문 내용 추출
        sections = []
        try:
            content_element = driver.find_element(By.CSS_SELECTOR, "div.textlist.mt40#content")
            paragraphs = content_element.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if text:
                    sections.append(text)

            # 테이블 내의 텍스트도 포함
            table_cells = content_element.find_elements(By.TAG_NAME, "td")
            for td in table_cells:
                text = td.text.strip()
                if text and text not in sections:
                    sections.append(text)

        except Exception as e:
            print(f"Content Extraction Error for {url}: {e}")

        # JSON 데이터 구조화
        content_data = {
            "title": title,
            "department": department,
            "sections": sections
        }

        # 파일명 생성
        filename = f"{title}.json".replace("/", "_")
        output_path = os.path.join(output_dir, filename)

        # JSON 파일 저장
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(content_data, output_file, ensure_ascii=False, indent=4)

        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {url}: {e}")

driver.quit()