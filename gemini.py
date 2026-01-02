import requests
from score_calculation import *

# =========================
# Gemini RAG 컨텍스트
#  + 유사고객 리뷰 3건 포함
# =========================
def build_rag_context(reco_list):
    ctx_blocks = []

    for item in reco_list:
        p = item["product"]
        b = item["brand"]

        hw_pos = ", ".join(list(p["hwahae"]["positive"].keys())[:5])
        hw_neg = ", ".join(list(p["hwahae"]["negative"].keys())[:5])

        similar_reviews = "\n".join(
            [f"- {r['review_text']} (★{r['overall_rating']})"
             for r in item["similar_reviews"]]
        )

        block = f"""
[브랜드]
- {b["brand_name"]}
- CRM 톤: {b["crm_tone"]}
- 메시지 목적: {b["crm_purpose"]}

[제품]
- 제품명: {p["product_name"]}
- 특징 태그: {", ".join(p["tags"])}
- 기획상품 여부: {"기획상품" if p["is_planning_product"] else "일반상품"}

[제품 설명 프롬프트]
{p["feature_prompt_text"]}

[화해 긍정 키워드] {hw_pos}
[화해 부정 키워드] {hw_neg}

[고객님과 유사한 사용자는 이런 평가를 남겼습니다]
{similar_reviews}
"""
        ctx_blocks.append(block)

    return "\n\n--------------------\n\n".join(ctx_blocks)


# =========================
# Gemini 메시지 생성
# =========================
def generate_marketing_message(context, customer):

    prompt = f"""
당신은 아모레몰 CRM 개인화 추천 카피라이팅 AI입니다.

추천 단위는 "제품"이며,
문장 톤과 메시지 목적은
해당 제품의 브랜드 CRM 전략을 따릅니다.

[고객 기본 정보]
- 연령대: {customer["age_group"]}
- 성별: {customer["gender"]}

[추천 제품 + CRM 컨텍스트]
{context}

작성 규칙:
- 고객과 유사 사용자 리뷰를 근거로 추천 사유를 설명
- "고객님과 유사한 사용자는 이런 평을 남겼다" 문단 포함
- 마지막에 "이런 이유로 추천드립니다"로 결론 작성
- 과장 / 추정 / 단정 표현 금지
"""
    print("\n\n\n\n\n\n\n")
    print(prompt)
    print("\n\n\n\n\n\n\n")
    payload = {"contents":[{"parts":[{"text": prompt}]}]}

    res = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json=payload,
    )
    res.raise_for_status()

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]