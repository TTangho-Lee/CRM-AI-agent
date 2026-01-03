from collections import defaultdict
import random
import re
from score_calculation import *
from gemini import *

# =========================
# 언어 감지
# =========================
def detect_language(name):
    if re.search("[\u4e00-\u9FFF]", name):
        return "zh"
    elif re.search("[a-zA-Z]", name):
        return "en"
    else:
        return "ko"

# =========================
# 고객 성향 요약
# =========================
def build_customer_profile(customer):
    purchases = customer["purchases"]

    if not purchases:
        return {
            "avg_price_paid": 0,
            "avg_discount_rate": 0,
            "planning_liking": 0,
            "category_pref": {},
            "purchased_ids": set(),
            "pick_list": customer.get("pick_list", []),
            "basket": customer.get("basket", []),
            "num_purchases": 0
        }

    avg_price = sum(p["price_paid"] for p in purchases) / len(purchases)
    avg_discount = sum(p["discount_rate"] for p in purchases) / len(purchases)

    planning_count = 0
    category_pref = defaultdict(int)

    for p in purchases:
        product = load_product(p["product_id"])

        category = product.get("category")
        if category:
            category_pref[category] += 1

        if product.get("is_planning_product"):
            planning_count += 1

    planning_ratio = planning_count / len(purchases)

    return {
        "avg_price_paid": avg_price,
        "avg_discount_rate": avg_discount,

        "planning_liking": planning_ratio,
        "category_pref": dict(category_pref),

        "purchased_ids": set(p["product_id"] for p in purchases),

        "pick_list": customer.get("pick_list", []),
        "basket": customer.get("basket", []),

        "num_purchases": len(purchases)
    }


# =========================
# ✦ 고객과 유사 + 별점 높은 리뷰 3개 선택
#   (연령 / 성별 / 카테고리 성향 기반)
# =========================
def pick_top_similar_reviews(product, customer, profile, top_k=5):
    reviews = product.get("reviews", [])
    scored = []

    for r in reviews:
        sim = 0

        # 연령대 유사
        if r.get("age_group") == customer.get("age_group"):
            sim += 1

        # 성별 유사
        if r.get("gender") == customer.get("gender"):
            sim += 1

        # 카테고리 성향 유사
        if r.get("main_category") in profile["category_pref"]:
            sim += 1

        scored.append({
            "review": r,
            "score": sim,
            "rating": r.get("overall_rating", 0)
        })

    ranked = sorted(scored, key=lambda x: (x["score"], x["rating"]), reverse=True)
    return [x["review"] for x in ranked[:top_k]]

# =========================
# 추천 후보 생성
# =========================
def recommend_products(customer_id, top_k=5):
    customer = load_customer(customer_id)
    brands = load_brands()
    profile = build_customer_profile(customer)

    results = []

    for brand in load_json(BRAND_DB):
        for pid in brand["product_ids"]:
            product = load_product(pid)

            if pid in profile["purchased_ids"]:
                continue

            score, details = compute_product_match_score(product, customer, profile)

            results.append({
                "product": product,
                "brand": brands[product["brand_id"]],
                "score": score,
                "details": details,
                "similar_reviews": pick_top_similar_reviews(product, customer, profile)
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    # top_k 후보 풀 만들기
    top_candidates = results[:top_k]

    # 그중 하나 랜덤 선택
    chosen = random.choice(top_candidates)

    # 기존 인터페이스 유지 (리스트 형태로 반환)
    return [chosen], customer, profile

# =========================
# 메인 실행
# =========================
if __name__ == "__main__":
    # 테스트할 사용자 ID 리스트 (U001: 한국어, U005, 6: 영어, U007: 중국어)
    test_users = ["U006", "U007"]

    for USER_ID in test_users:
        print(f"\n\n##########################################################")
        print(f"Processing User: {USER_ID}")
        print(f"##########################################################\n")

        reco, customer, profile = recommend_products(USER_ID)
        context = build_rag_context(reco)

        lang = detect_language(customer["user_name"])
        print(f"Detected Language for {customer['user_name']}: {lang}")

        print("\n=== 🔎 추천 제품 점수 분석 ===\n")
        for r in reco:
            p = r["product"]
            d = r["details"]

            print(f"- {p['product_name']}")
            print(f"  ▶ feature score (합=1): {d['feature_score']}")
            print(f"  ▶ review affinity (가중치=1): {d['review_affinity']['score']}")
            print(f"  ▶ 최종 점수 (0~2): {d['final_score']}")
            print(f"  ▶ 유사 고객 리뷰:")
            for rv in r["similar_reviews"]:
                print(f"    - {rv['review_text']} (★{rv['overall_rating']})")
            print("")

        message = generate_marketing_message(context, customer, language=lang)

        print("\n=== 📨 생성된 CRM 개인화 메시지 ===\n")
        print(message)
