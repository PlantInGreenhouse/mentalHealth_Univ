import os
import json

def merge_json_files(input_folder, output_file):
    merged_data = []

    # 폴더 내의 모든 파일을 순회
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        # 확장자가 .json 인 파일만 읽기
        if filename.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    merged_data.append(data)
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, skipping...")

    # 병합된 데이터를 새로운 JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(merged_data, outfile, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_folder = "data/raw"
    output_file = "data/merged.json"
    merge_json_files(input_folder, output_file)
    print(f"Merged JSON saved to {output_file}")