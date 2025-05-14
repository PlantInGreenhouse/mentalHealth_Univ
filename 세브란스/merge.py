import os
import json

# JSON 파일들이 저장된 디렉터리 경로
INPUT_DIR = "data/disease_data"
OUTPUT_FILE = "data/merged_data.json"

def merge_json_files(input_dir, output_file):
    """여러 JSON 파일을 병합하여 하나의 JSON 파일로 저장"""
    merged_data = []

    # 모든 JSON 파일을 순회
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    merged_data.append(data)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON file {filename}: {e}")

    # 병합된 데이터를 저장
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(merged_data, outfile, ensure_ascii=False, indent=4)

    print(f"Merged data saved to {output_file}")

if __name__ == "__main__":
    merge_json_files(INPUT_DIR, OUTPUT_FILE)