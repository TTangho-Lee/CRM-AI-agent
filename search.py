import os
import json
import requests
from collections import defaultdict

# Gemini API
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-pro:generateContent"
)

# 경로
AMORE_DIR = "아모레퍼시픽 json 데이터베이스"
HWAHAE_DIR = "화해 json 데이터베이스"
USER_PROFILE_DIR = "user_profiles"
USER_PURCHASE_DIR = "user_purchases"
PRICE_DB_PATH = "current_prices.json"

# 함수
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_price_db():
    return {p["product_id"]: p for p in load_json(PRICE_DB_PATH)}

def is_similar_user(review, user_feat):
    if review["age_group"] != user_feat["age_group"]:
        return False
    if review.get("gender") != user_feat.get("gender"):
        return False
    if not set(review["skin_features"]) & set(user_feat["skin_features"]):
        return False
    return True

def collect_similar_user_reviews(product_id, user_feat, max_reviews=3):
    reviews = load_json(os.path.join(AMORE_DIR, f"{product_id}.json"))
    texts = []

    for r in reviews:
        if is_similar_user(r, user_feat):
            texts.append(r["review_text"].strip())
        if len(texts) >= max_reviews:
            break

    return texts

# 1️ 제품 Feature
def build_product_feature(product_id):
    reviews = load_json(os.path.join(AMORE_DIR, f"{product_id}.json"))
    hwahae = load_json(os.path.join(HWAHAE_DIR, f"{product_id}.json"))

    age_scores = defaultdict(list)
    skin_scores = defaultdict(list)
    rating_norm = defaultdict(lambda: defaultdict(int))

    for r in reviews:
        age_scores[r["age_group"]].append(r["overall_rating"])

        for s in r["skin_features"]:
            skin_scores[s].append(r["overall_rating"])

        for k, v in r["ratings_norm"].items():
            rating_norm[k][v] += 1

    return {
        "age_avg": {k: sum(v)/len(v) for k, v in age_scores.items()},
        "skin_avg": {k: sum(v)/len(v) for k, v in skin_scores.items()},
        "rating_norm": rating_norm,
        "hwahae_positive": hwahae["positive"],
        "hwahae_negative": hwahae["negative"]
    }

# 2️ 구매 기반 유저 취향
def build_user_preference_from_purchases(purchases):
    skin_pref = defaultdict(list)
    hwahae_pos = defaultdict(int)
    hwahae_neg = defaultdict(int)

    for p in purchases["purchases"]:
        pid = p["product_id"]
        feat = build_product_feature(pid)

        for k, v in feat["skin_avg"].items():
            skin_pref[k].append(v)

        for k, v in feat["hwahae_positive"].items():
            hwahae_pos[k] += v

        for k, v in feat["hwahae_negative"].items():
            hwahae_neg[k] += v

    return {
        "skin_pref": {k: sum(v)/len(v) for k, v in skin_pref.items()},
        "hwahae_positive": dict(hwahae_pos),
        "hwahae_negative": dict(hwahae_neg)
    }


# 3️ 가격/할인 성향
def build_user_price_preference(purchases):
    discounts = [p["discount_rate"] for p in purchases["purchases"]]
    prices = [p["price_paid"] for p in purchases["purchases"]]

    return {
        "avg_discount": sum(discounts)/len(discounts),
        "min_discount": min(discounts),
        "max_discount": max(discounts),
        "avg_price": sum(prices)/len(prices)
    }


# 4️ 유저 Feature
def build_user_feature(user_id):
    profile = load_json(os.path.join(USER_PROFILE_DIR, f"{user_id}.json"))
    purchases = load_json(os.path.join(USER_PURCHASE_DIR, f"{user_id}.json"))

    return {
        "age_group": profile["age_group"],
        "skin_features": profile["skin_features"],
        "preference": build_user_preference_from_purchases(purchases),
        "price_pref": build_user_price_preference(purchases),
        "purchased_ids": {p["product_id"] for p in purchases["purchases"]}
    }


# 5️ 점수 계산 함수
def compute_purchase_similarity(product_feat, user_pref):
    score, cnt = 0, 0
    for skin, val in user_pref["skin_pref"].items():
        if skin in product_feat["skin_avg"]:
            score += product_feat["skin_avg"][skin] * val
            cnt += 1
    return score / cnt if cnt else 0


def discount_similarity(product_discount, user_price_pref):
    return 1 - abs(product_discount - user_price_pref["avg_discount"])


def pass_price_filter(price, user_price_pref):
    return (
        user_price_pref["avg_price"] * 0.5
        <= price
        <= user_price_pref["avg_price"] * 1.5
    )


def compute_score(product_feat, price_info, user_feat):
    if not pass_price_filter(
        price_info["current_price"], user_feat["price_pref"]
    ):
        return None

    score = 0

    score += compute_purchase_similarity(
        product_feat, user_feat["preference"]
    ) * 0.4

    skin_score = sum(
        product_feat["skin_avg"].get(s, 3)
        for s in user_feat["skin_features"]
    ) / len(user_feat["skin_features"])
    score += skin_score * 0.3

    score += discount_similarity(
        price_info["discount_rate"],
        user_feat["price_pref"]
    ) * 0.3

    return score

# 6️ 추천 실행
def recommend_products(user_id, top_k=3):
    user_feat = build_user_feature(user_id)
    price_db = load_price_db()

    results = []

    for fname in os.listdir(AMORE_DIR):
        pid = fname.replace(".json", "")

        if pid in user_feat["purchased_ids"]:
            continue
        if pid not in price_db:
            continue

        product_feat = build_product_feature(pid)
        score = compute_score(
            product_feat, price_db[pid], user_feat
        )

        if score is not None:
            results.append((pid, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k], user_feat


# 7️ RAG 컨텍스트
def build_rag_context(products, user_feat):
    contexts = []

    for pid, score in products:
        hwahae = load_json(os.path.join(HWAHAE_DIR, f"{pid}.json"))
        similar_reviews = collect_similar_user_reviews(pid, user_feat)

        ctx = f"""
제품명: {pid}
추천 점수: {score:.2f}

[화해 긍정 키워드]
{", ".join(list(hwahae["positive"].keys())[:5])}

[화해 부정 키워드]
{", ".join(list(hwahae["negative"].keys())[:5])}
"""

        if similar_reviews:
            ctx += "\n[비슷한 고객 리뷰]\n"
            for i, txt in enumerate(similar_reviews, 1):
                ctx += f"- ({i}) {txt}\n"

        contexts.append(ctx)

    return "\n\n".join(contexts)



# 8️ Gemini 메시지 생성
def generate_message(context, user_feat):
    prompt = f"""
당신은 아모레퍼시픽 공식몰 마케팅 AI입니다.

[고객 정보]
- 연령대: {user_feat["age_group"]}
- 피부 특징: {", ".join(user_feat["skin_features"])}

[추천 제품 정보]
{context}

고객의 과거 구매 성향과 가격 조건을 고려한
신뢰감 있는 추천 메시지를 작성하세요.
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    res = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json=payload
    )

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == "__main__":
    USER_ID = "U001"

    products, user_feat = recommend_products(USER_ID)
    context = build_rag_context(products)
    message = generate_message(context, user_feat)

    print("\n추천 결과")
    for p in products:
        print(p)

    print("\n추천 메시지")
    print(message)
