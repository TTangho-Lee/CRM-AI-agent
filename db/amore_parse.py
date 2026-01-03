import json
import os
import re


TXT_DIR = "db/리뷰 txt/"
JSON_DIR = "db/리뷰 json/"


REVIEW_SPLITTER = "\n\n\n\n\n"
'''
TARGET_PRODUCT_NAME = "루즈 클래시 3.5g"
RATING_KEYS = ["제형", "지속력", "발색감","피부톤"]

TARGET_PRODUCT_NAME = "UV프로텍터 톤업 SPF50+PA++++ 50ml"
RATING_KEYS = ["사용성", "민감성", "발림성"]

TARGET_PRODUCT_NAME = "[듀오] NEW 블랙 쿠션 파운데이션 SPF34PA++ (본품15g+리필15g)"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "자연을 닮은 립밤"
RATING_KEYS = ["지속력", "유분기", "촉촉함"]

TARGET_PRODUCT_NAME = "랩핑 마스크 기획세트 4매 (+1매 증정)"
RATING_KEYS = ["보습감", "향", "민감성"]

TARGET_PRODUCT_NAME = "세라마이드 아토 6.0 탑투토워시 500ml"
RATING_KEYS = ["용량", "민감성", "향기"]

TARGET_PRODUCT_NAME = "NEW [대용량] 세라마이드 아토 로션 564ml"
RATING_KEYS = ["용량", "민감성", "향기"]

TARGET_PRODUCT_NAME = "노세범 미네랄 파우더 5g"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "아이 코어 팔레트 9g"
RATING_KEYS = ["발색감", "지속력", "사용감"]

TARGET_PRODUCT_NAME = "[2개이상구매시10%추가할인][NEW] 왓츠 인 마이 아이즈"
RATING_KEYS = ["발색감", "지속력", "사용감"]

TARGET_PRODUCT_NAME = "드로잉 아이 브로우 0.25g"
RATING_KEYS = ["발색감", "지속력", "사용감"]

TARGET_PRODUCT_NAME = "슈퍼바이탈 기초 2종 세트 (150ml+150ml)"
RATING_KEYS = ["보습감", "향", "민감성"]

TARGET_PRODUCT_NAME = "비타민C 엑스퍼트25% 토닝앰플 23ml"
RATING_KEYS = ["보습감", "향", "민감성"]

TARGET_PRODUCT_NAME = "맨 올데이 퍼펙트 올인원 120ml"
RATING_KEYS = ["민감성", "향", "보습감"]

TARGET_PRODUCT_NAME = "자음2종 세트 (150ml+125ml)"
RATING_KEYS = ["보습감", "향", "민감성"]

TARGET_PRODUCT_NAME = "자음유액 EX 125ml"
RATING_KEYS = ["보습감", "향", "민감성"]

TARGET_PRODUCT_NAME = "립 슬리핑 마스크 EX 20g"
RATING_KEYS = ["지속력", "유분기", "촉촉함"]

TARGET_PRODUCT_NAME = "[도넛립세럼] 글레이즈 크레이즈 틴티드 립 세럼 (8종) 12g"
RATING_KEYS = ["지속력", "유분기", "촉촉함"]



TARGET_PRODUCT_NAME = "이지 블렌딩 컨실러 10g"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "라이트 피팅 컨실러 다크서클 커버 7g"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "젤 크림스킨 스페셜 기프트 세트 (본품 170ml+증정50ml)"
RATING_KEYS = ["보습감", "향", "민감성"]

TARGET_PRODUCT_NAME = "네오 쿠션 뮤이 더블 SPF42PA++ 15g2"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "순행클렌징오일 200ml"
RATING_KEYS = ["세정력", "촉촉함", "민감성"]

TARGET_PRODUCT_NAME = "퍼펙팅 쿠션 에어리 트리플 (17N1호21N1호) SPF50+PA+++"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "픽싱틴트 4g"
RATING_KEYS = ["제형", "지속력", "발색감","피부톤"]

TARGET_PRODUCT_NAME = "디어 달링 워터젤 틴트"
RATING_KEYS = ["제형", "지속력", "발색감","피부톤"]

TARGET_PRODUCT_NAME = "플레이 멀티 아이즈"
RATING_KEYS = ["발색감", "지속력", "사용감"]

TARGET_PRODUCT_NAME = "비벨벳 파운데이션 SPF22PA++"
RATING_KEYS = ["커버력", "지속력", "피부 표현", "피부톤"]

TARGET_PRODUCT_NAME = "리얼 아이 팔레트"
RATING_KEYS = ["발색감", "지속력", "사용감"]

TARGET_PRODUCT_NAME = "[디즈니에디션] 아이 코어 팔레트 기획세트"
RATING_KEYS = ["발색감", "지속력", "사용감"]

TARGET_PRODUCT_NAME = "노웨어 립스틱 바밍글로우 3g"
RATING_KEYS = ["제형", "지속력", "발색감","피부톤"]

TARGET_PRODUCT_NAME = "올리브 비타민 E 리얼 클렌징 티슈 30매"
RATING_KEYS = ["세정력", "촉촉함", "민감성"]

'''


TARGET_PRODUCT_NAME = "리얼 아이 팔레트"
RATING_KEYS = ["발색감", "지속력", "사용감"]

















def extract_overall_rating_from_filename(filename: str):
    m = re.search(r"별점([1-5])", filename)
    return int(m.group(1)) if m else None


def parse_review_block(block: str, overall_rating: int):
    lines = [l.rstrip() for l in block.splitlines()]

    # 너무 짧으면 스킵
    if len(lines) < 5:
        return None

    # ─────────────────────────────
    # 1) gender 줄 위치 찾기
    # ─────────────────────────────
    gender_idx = None
    for i, line in enumerate(lines):
        t = line.strip()
        if t in ("여성", "남성"):
            gender_idx = i
            break

    if gender_idx is None:
        # gender 줄이 없으면 파싱하지 않음
        return None

    # ─────────────────────────────
    # 2) gender 기준으로 주변 필드 추출
    # ─────────────────────────────
    age_group = lines[gender_idx - 1].strip() if gender_idx - 1 >= 0 else ""

    skin_features = []
    if gender_idx + 1 < len(lines):
        skin_features.append(lines[gender_idx + 1].strip())
    if gender_idx + 2 < len(lines):
        skin_features.append(lines[gender_idx + 2].strip())

    result = {
        "overall_rating": overall_rating,
        "age_group": age_group,
        "gender": lines[gender_idx].strip(),
        "skin_features": skin_features,
        "ratings_norm": {},
        "review_text": "",
    }

    # ─────────────────────────────
    # 3) 나머지 평점 키 탐색 (기존 로직 그대로)
    # ─────────────────────────────
    last_rating_value_idx = -1
    i = 0

    while i < len(lines) - 1:
        key = lines[i].strip()
        if key in RATING_KEYS:
            value = lines[i + 1].strip()
            result["ratings_norm"][key] = value
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
            block = block.strip()
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
