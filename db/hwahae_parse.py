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
        txt_path="db/화해 txt/랩핑 마스크 기획세트 4매 (+1매 증정).txt",
        output_json_path="db/화해 json/랩핑 마스크 기획세트 4매 (+1매 증정).json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/드로잉 아이 브로우 0.25g.txt",
        output_json_path="db/화해 json/드로잉 아이 브로우 0.25g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/노세범 미네랄 파우더 5g.txt",
        output_json_path="db/화해 json/노세범 미네랄 파우더 5g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/UV프로텍터 톤업 SPF50+PA++++ 50ml.txt",
        output_json_path="db/화해 json/UV프로텍터 톤업 SPF50+PA++++ 50ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/NEW [대용량] 세라마이드 아토 로션 564ml.txt",
        output_json_path="db/화해 json/NEW [대용량] 세라마이드 아토 로션 564ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/[듀오] NEW 블랙 쿠션 파운데이션 SPF34PA++ (본품15g+리필15g).txt",
        output_json_path="db/화해 json/[듀오] NEW 블랙 쿠션 파운데이션 SPF34PA++ (본품15g+리필15g).json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/[도넛립세럼] 글레이즈 크레이즈 틴티드 립 세럼 (8종) 12g.txt",
        output_json_path="db/화해 json/[도넛립세럼] 글레이즈 크레이즈 틴티드 립 세럼 (8종) 12g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/루즈 클래시 3.5g.txt",
        output_json_path="db/화해 json/루즈 클래시 3.5g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/립 슬리핑 마스크 EX 20g.txt",
        output_json_path="db/화해 json/립 슬리핑 마스크 EX 20g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/맨 올데이 퍼펙트 올인원 120ml.txt",
        output_json_path="db/화해 json/맨 올데이 퍼펙트 올인원 120ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/비타민C 엑스퍼트25% 토닝앰플 23ml.txt",
        output_json_path="db/화해 json/비타민C 엑스퍼트25% 토닝앰플 23ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/세라마이드 아토 6.0 탑투토워시 500ml.txt",
        output_json_path="db/화해 json/세라마이드 아토 6.0 탑투토워시 500ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/슈퍼바이탈 기초 2종 세트 (150ml+150ml).txt",
        output_json_path="db/화해 json/슈퍼바이탈 기초 2종 세트 (150ml+150ml).json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/아이 코어 팔레트 9g.txt",
        output_json_path="db/화해 json/아이 코어 팔레트 9g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/왓츠 인 마이 아이즈.txt",
        output_json_path="db/화해 json/왓츠 인 마이 아이즈.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/자연을 닮은 립밤.txt",
        output_json_path="db/화해 json/자연을 닮은 립밤.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/자음2종 세트 (150ml+125ml).txt",
        output_json_path="db/화해 json/자음2종 세트 (150ml+125ml).json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/자음유액 EX 125ml.txt",
        output_json_path="db/화해 json/자음유액 EX 125ml.json"
    )
    



    parse_ai_review_summary(
        txt_path="db/화해 txt/순행클렌징오일 200ml.txt",
        output_json_path="db/화해 json/순행클렌징오일 200ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/퍼펙팅 쿠션 에어리 트리플 (17N1호21N1호) SPF50+PA+++.txt",
        output_json_path="db/화해 json/퍼펙팅 쿠션 에어리 트리플 (17N1호21N1호) SPF50+PA+++.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/픽싱틴트 4g.txt",
        output_json_path="db/화해 json/픽싱틴트 4g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/디어 달링 워터젤 틴트.txt",
        output_json_path="db/화해 json/디어 달링 워터젤 틴트.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/플레이 멀티 아이즈.txt",
        output_json_path="db/화해 json/플레이 멀티 아이즈.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/비벨벳 파운데이션 SPF22PA++.txt",
        output_json_path="db/화해 json/비벨벳 파운데이션 SPF22PA++.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/이지 블렌딩 컨실러 10g.txt",
        output_json_path="db/화해 json/이지 블렌딩 컨실러 10g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/리얼 아이 팔레트.txt",
        output_json_path="db/화해 json/리얼 아이 팔레트.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/[디즈니에디션] 아이 코어 팔레트 기획세트.txt",
        output_json_path="db/화해 json/[디즈니에디션] 아이 코어 팔레트 기획세트.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/노웨어 립스틱 바밍글로우 3g.txt",
        output_json_path="db/화해 json/노웨어 립스틱 바밍글로우 3g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/올리브 비타민 E 리얼 클렌징 티슈 30매.txt",
        output_json_path="db/화해 json/올리브 비타민 E 리얼 클렌징 티슈 30매.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/라이트 피팅 파운데이션 SPF20PA++ 30ml.txt",
        output_json_path="db/화해 json/라이트 피팅 파운데이션 SPF20PA++ 30ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/라이트 피팅 컨실러 다크서클 커버 7g.txt",
        output_json_path="db/화해 json/라이트 피팅 컨실러 다크서클 커버 7g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/에어리매트 틴트 3.8g.txt",
        output_json_path="db/화해 json/에어리매트 틴트 3.8g.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/히알루론 모이스춰 수분크림 100ml.txt",
        output_json_path="db/화해 json/히알루론 모이스춰 수분크림 100ml.json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/젤 크림스킨 스페셜 기프트 세트 (본품 170ml+증정50ml).txt",
        output_json_path="db/화해 json/젤 크림스킨 스페셜 기프트 세트 (본품 170ml+증정50ml).json"
    )
    parse_ai_review_summary(
        txt_path="db/화해 txt/네오 쿠션 뮤이 더블 SPF42PA++ 15g2.txt",
        output_json_path="db/화해 json/네오 쿠션 뮤이 더블 SPF42PA++ 15g2.json"
    )
    