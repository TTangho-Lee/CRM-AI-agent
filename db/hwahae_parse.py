import json


def parse_ai_review_summary(txt_path, output_json_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    result = {
        "positive": {},
        "negative": {}
    }

    mode = None  # positive / negative
    i = 0

    while i < len(lines):
        line = lines[i]

        if line == "좋아요":
            mode = "positive"
            i += 1
            continue

        if line == "아쉬워요":
            mode = "negative"
            i += 1
            continue

        # 필요없는 타이틀 제거
        if line in ("AI가 분석한 리뷰", "타이틀 아이콘"):
            i += 1
            continue

        if mode and i + 1 < len(lines):
            keyword = line
            count_line = lines[i + 1]

            if count_line.replace(",", "").isdigit():
                result[mode][keyword] = int(count_line.replace(",", ""))
                i += 2
                continue

        i += 1

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("✅ AI 리뷰 요약 JSON 생성 완료")


if __name__ == "__main__":
    parse_ai_review_summary(
        txt_path="화해 txt 데이터베이스/[토리든] 다이브인 저분자 히알루론산 세럼 100ml 기획 (+수딩크림 50ml).txt",
        output_json_path="화해 json 데이터베이스/[토리든] 다이브인 저분자 히알루론산 세럼 100ml 기획 (+수딩크림 50ml).json"
    )
