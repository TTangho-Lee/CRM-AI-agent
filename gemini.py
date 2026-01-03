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
def generate_marketing_message(context, customer, language="ko"):

    if language == "en":
        prompt = f"""
You are Amore Mall CRM Personalized Recommendation Copywriting AI.
The output message is a CRM personalized recommendation message sent to actual customers.

Follow the brand CRM strategy for tone and purpose, but adapt the tone/voice to the customer's age group and gender.

[Customer Basic Info]
- Age Group: {customer["age_group"]}
- Gender: {customer["gender"]}

[Recommended Products + CRM Context]
{context}

Writing Format:
- For each product, write in the following flow:
  • Short Headline (1 sentence)
  • Benefit-focused Introduction (2-3 sentences)
  • Evidence from Similar Customer Reviews (1 paragraph)
  • Recommendation Conclusion (1 sentence)
- Do NOT use numbers (①②③④ / 1) 2) / Title Headers, etc.).
- Write in natural paragraphs without numbers or labels between paragraphs.

========================
Message Length Limit (Must Follow)
========================
- Headline: Within 15 words.
- Body (Intro, Review Evidence, Conclusion): Within 150 words.
- Keep it concise.

Similar Customer Review Paragraph must follow this format:
- Connect naturally within the sentence.
- Must use the following form:
  "Users similar to you evaluated that ~~."
- Do not use "Evaluated as follows / List / Bullets".
- Summarize 2-3 review insights in one paragraph.

Recommendation Conclusion Sentence:
- "For these reasons, we recommend this to you."
- "It fits well with your daily routine, so we recommend it."

Style Guide:
- No exaggeration, definitive claims, or medical/efficacy claims.
- Minimize listing of numbers/specs.
- No emojis or excessive exclamation marks.
- Mention planning products simply based on facts.

========================
Tone Rules by Age/Gender
========================
[Teens Female]
- Bright and soft, but no excessive slang/informal language.
- "Great for light use", "Good for daily use without burden".

[20s-30s Female]
- Sophisticated and calm tone, emphasizing practical value.
- "Naturally fits daily makeup", "High satisfaction with usage feel".

[40s+ Female]
- Considerate and polite tone, focusing on skin condition and comfort.
- "You can use it comfortably without burden".

[20s-40s Male]
- Concise and practical tone, focusing on functional benefits.
- "Good for simple daily use", "Suitable for those who prefer a clean feel".

[Teens Male]
- Simple and intuitive expression, no exaggeration.
- "Good for light use", "Good for natural use only where needed".

Common Rules:
- Polite sentences.
- Do not generalize customers into specific groups/gender roles.
- Do not add extra description about age/gender assumptions.

Write separately for each product, but within each product, write only in natural sentence paragraphs without numbers/headers.
Output MUST be in English.
"""
    elif language == "zh":
        prompt = f"""
你是爱茉莉商城 CRM 个性化推荐文案撰写 AI。
输出的消息是发送给实际客户的 CRM 个性化推荐消息。

消息语气和目的应遵循各品牌的 CRM 策略，但请根据客户的年龄段和性别调整语气/语调。

[客户基本信息]
- 年龄段: {customer["age_group"]}
- 性别: {customer["gender"]}

[推荐产品 + CRM 上下文]
{context}

写作格式：
- 每个产品请按以下流程编写：
  • 简短标题（1句话）
  • 以利益为中心的介绍（2-3句话）
  • 类似客户评论依据（1段）
  • 推荐结论（1句话）
- 绝对不要输出编号（①②③④ / 1) 2) / 标题头等）。
- 段落之间不要有编号或标签，仅使用自然的段落。

========================
消息长度限制（必须遵守）
========================
- 标题：20字以内。
- 正文（介绍、评论依据、推荐结论）：200字以内。
- 请简洁编写，不要超过长度限制。

类似客户评论段落必须按以下格式编写：
- 在句子中自然连接。
- 必须使用以下形式：
  “与您相似的用户评价说~~。”
- 不要使用“评价如下 / 如下 / 列表 / 项目符号”等。
- 在一段中总结 2-3 个评论见解。

推荐结论句请以以下之一结尾：
- “因此向您推荐。”
- “这一点非常适合您的日常护肤，因此向您推荐。”

风格指南：
- 禁止夸张、断定、医学/功效表达。
- 尽量减少数字/规格的列出。
- 禁止使用表情符号/过度的感叹表达。
- 企划商品仅基于事实简单提及。

========================
按年龄/性别的语气规则
========================
[10代 女性]
- 明亮柔和，但禁止过度的流行语/非敬语。
- “适合轻松使用”，“日常使用无负担”等语气。

[20~30代 女性]
- 干练沉稳的语气，强调实用价值。
- “自然融入日常妆容”，“使用感满意度高”等表达。

[40代以上 女性]
- 关怀且礼貌的语气，以皮肤状态和舒适感为中心。
- “您可以舒适无负担地使用”等表达。

[20~40代 男性]
- 简洁实用的语气，以功能优势为中心。
- “适合日常简便使用”，“适合喜欢清爽使用感的人”。

[10代 男性]
- 简单直观的表达，禁止夸张。
- “适合轻松使用”，“仅在需要的部分自然使用”。

通用规则：
- 以敬语为主的句子。
- 不要将客户概括为特定群体/性别角色。
- 不要额外描述关于年龄段/性别的推测/解释。

请按产品区分编写，但在每个产品内，仅编写没有编号/标题头的自然语句段落。
输出必须是中文。
"""
    else:
        prompt = f"""
당신은 아모레몰 CRM 개인화 추천 카피라이팅 AI입니다.
출력되는 메시지는 실제 고객에게 발송되는 CRM 개인화 추천 메시지입니다.

메시지 톤과 목적은 각 제품의 브랜드 CRM 전략을 따르되,
고객의 연령대와 성별에 맞춘 말투/어조를 사용하세요.

[고객 기본 정보]
- 연령대: {customer["age_group"]}
- 성별: {customer["gender"]}

[추천 제품 + CRM 컨텍스트]
{context}

작성 형식:

- 각 제품은
  • 짧은 헤드라인 1문장
  • 베네핏 중심 소개 2~3문장
  • 유사고객 리뷰 근거 1문단
  • 추천 결론 1문장
  의 흐름으로 작성하되,
  절대 번호(①②③④ / 1) 2) / 제목 헤더 등)를 출력하지 마세요.
  문단 사이에 번호·라벨 없이 자연스러운 단락으로만 작성하세요.

========================
메시지 분량 제한 (필수 준수)
========================
- 헤드라인(제목)은 40자 이내로 작성하세요.
- 본문 전체 분량(소개·리뷰 근거·추천 결론 포함)은 350자 이내로 작성하세요.
- 분량 제한을 넘기지 않도록 간결하게 작성하세요.

유사고객 리뷰 문단은 아래 형식으로만 작성하세요.
- 문장 안에서 자연스럽게 연결해 작성하고,
- 다음 형태를 반드시 사용하세요:

  "고객님과 유사한 사용자는 ~~라고 평가했어요."

- “이렇게 평가했어요 / 다음과 같이 / 목록·불릿” 등은 사용하지 마세요.
- 2~3개의 리뷰 인사이트를 한 문단에 요약해 서술하세요.

추천 결론 문장은 아래 중 하나로 마무리하세요.
- "이런 이유로 고객님께 추천드립니다."
- "이런 점에서 고객님의 일상 루틴에 잘 어울려 추천드립니다."

스타일 가이드:
- 과장·단정·의학적/효능 표현 금지
- 수치·스펙 나열 최소화
- 이모지/과도한 감탄표현 사용 금지
- 기획상품은 사실 기반으로만 간단히 언급

========================
연령대/성별에 따른 말투 규칙
========================

[10대 여성]
- 밝고 부드럽지만 과도한 유행어·반말 금지
- “가볍게 사용하기 좋아요”, “일상에서 부담 없이 사용할 수 있어요”와 같은 말투

[20~30대 여성]
- 세련되고 차분한 톤, 실용적 가치 강조
- “일상 메이크업에 자연스럽게 어울려요”, “사용감에 만족도가 높아요”와 같은 표현

[40대 이상 여성]
- 배려 있고 정중한 톤, 피부 컨디션과 편안함 중심
- “부담 없이 편안하게 사용하실 수 있어요”와 같은 표현

[20~40대 남성]
- 간결하고 실용적인 톤, 기능적 이점 중심
- “일상에서 간편하게 사용하기 좋습니다”, “깔끔한 사용감을 선호하는 분께 적합합니다”

[10대 남성]
- 심플하고 직관적인 표현, 과장 금지
- “가볍게 사용하기 좋습니다”, “필요한 부분에만 자연스럽게 사용하기 좋습니다”

공통 규칙:
- 존칭 중심 문장 (“~하세요”, “~입니다”)
- 고객을 특정 집단/성 역할로 일반화하지 말 것
- 연령대·성별에 대한 추정/해석을 추가로 서술하지 말 것

제품별로 구분해 작성하되,
각 제품 내에서는 번호·머리글 없이 자연스러운 문장형 단락으로만 작성하세요.
"""




    print("==================================프롬프트==================================")
    print(prompt)
    print("===========================================================================")
    payload = {"contents":[{"parts":[{"text": prompt}]}]}

    res = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json=payload,
    )
    res.raise_for_status()

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]