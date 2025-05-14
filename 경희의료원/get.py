import requests
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://khmc.or.kr"
LIST_URL = "https://khmc.or.kr/kr/health-knowledge-medical-common/list.do?pageNo={}"
OUTPUT_FILE = "khmc_links.json"

def get_links_from_page(page_no):
    """페이지에서 질환 링크를 추출"""
    url = LIST_URL.format(page_no)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"페이지 {page_no} 접근 실패. 상태 코드: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = []

    # 'tbody#list' 내의 <a> 태그에서 링크 추출
    rows = soup.select("tbody#list a")
    for link in rows:
        relative_url = link.get("href")
        if relative_url and "view.do" in relative_url:
            full_url = BASE_URL + relative_url
            links.append(full_url)

    return links

def save_links(links, output_file):
    """링크를 JSON 파일로 저장"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(links, file, ensure_ascii=False, indent=4)
    print(f"✅ 링크 저장 완료: {output_file}")

def main():
    all_links = []

    for page_no in range(1, 4):
        print(f"📦 페이지 {page_no}에서 링크 추출 중...")
        page_links = get_links_from_page(page_no)
        all_links.extend(page_links)
        time.sleep(1)  # 서버에 부담을 주지 않기 위해 대기 시간 추가

    save_links(all_links, OUTPUT_FILE)

if __name__ == "__main__":
    main()