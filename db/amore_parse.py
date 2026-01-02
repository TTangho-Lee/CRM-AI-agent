import json
import os
import re


TXT_DIR = "아모레퍼시픽 txt 데이터베이스"
JSON_DIR = "아모레퍼시픽 json 데이터베이스"

# 처리할 제품명
TARGET_PRODUCT_NAME = "[설화수] NEW 자음생클렌징폼 150g"

REVIEW_SPLITTER = "\n\n\n\n\n"

RATING_KEYS = ["세정력", "촉촉함", "민감성"]

RATING_VALUE_MAP = {
    "세정력": {
        "잘 지워져요": "good",
        "적당해요": "neutral",
        "잔여감 있어요": "bad"
    },
    "촉촉함": {
        "촉촉해요": "good",
        "적당해요": "neutral",
        "당겨요": "bad"
    },
    "민감성": {
        "순해요": "good",
        "적당해요": "neutral",
        "자극적이에요": "bad"
    }
}


def extract_overall_rating_from_filename(filename: str):
    m = re.search(r"별점([1-5])", filename)
    return int(m.group(1)) if m else None


def normalize_rating(key, value):
    return RATING_VALUE_MAP.get(key, {}).get(value, "unknown")


def parse_review_block(block: str, overall_rating: int):
    lines = [l.rstrip() for l in block.splitlines()]

    if len(lines) < 10:
        return None

    result = {
        "overall_rating": overall_rating,
        "age_group": lines[3].strip(),
        "gender": lines[4].strip(),
        "skin_features": [
            lines[5].strip(),
            lines[6].strip()
        ],
        "ratings_raw": {},
        "ratings_norm": {},
        "review_text": ""
    }

    last_rating_value_idx = -1
    i = 0

    while i < len(lines) - 1:
        key = lines[i].strip()
        if key in RATING_KEYS:
            value = lines[i + 1].strip()
            result["ratings_raw"][key] = value
            result["ratings_norm"][key] = normalize_rating(key, value)
            last_rating_value_idx = i + 1
            i += 2
        else:
            i += 1

    if last_rating_value_idx == -1:
        return None

    review_start = last_rating_value_idx + 1

    review_end = len(lines)
    for i in range(len(lines) - 1, review_start, -1):
        if lines[i].strip() == "":
            review_end = i
            break

    review_body = lines[review_start:review_end]
    result["review_text"] = "\n".join(l.strip() for l in review_body).strip()

    return result


def main():
    os.makedirs(JSON_DIR, exist_ok=True)

    collected_reviews = []

    txt_files = [
        f for f in os.listdir(TXT_DIR)
        if f.endswith(".txt")
        and "별점" in f
        and f.startswith(TARGET_PRODUCT_NAME)
    ]

    if not txt_files:
        print(f"❌ '{TARGET_PRODUCT_NAME}'에 해당하는 txt 파일이 없습니다.")
        return

    print(f"🔍 처리 대상 파일 ({len(txt_files)}개):")
    for f in sorted(txt_files):
        print("  -", f)

    for txt_file in sorted(txt_files):
        overall_rating = extract_overall_rating_from_filename(txt_file)
        if overall_rating is None:
            continue

        txt_path = os.path.join(TXT_DIR, txt_file)
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = content.split(REVIEW_SPLITTER)

        for block in blocks:
            parsed = parse_review_block(block, overall_rating)
            if parsed:
                collected_reviews.append(parsed)

        print(f"📄 {txt_file} → 누적 리뷰 {len(collected_reviews)}개")

    output_path = os.path.join(JSON_DIR, f"{TARGET_PRODUCT_NAME}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collected_reviews, f, ensure_ascii=False, indent=2)

    print(f"\n최종 생성: {output_path}")
    print(f"총 리뷰 수: {len(collected_reviews)}")


if __name__ == "__main__":
    main()
