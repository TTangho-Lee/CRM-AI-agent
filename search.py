from collections import defaultdict
import random
from score_calculation import *
from gemini import *
import re

# =========================
# 고객 성향 요약
# =========================
def build_customer_profile(customer):
    purchases = customer["purchases"]

    # 구매 이력이 없는 경우 기본값 반환
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


def _normalize_text(s: str) -> str:
    """
    공백/개행/대소문자 차이를 제거하여
    동일 문장으로 간주할 수 있게 정규화
    """
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)   # 연속 공백 → 1칸
    return s.strip()

# =========================
# ✦ 고객과 유사 + 별점 높은 리뷰 k개 선택
#   (연령 / 성별 / 카테고리 성향 기반)
# =========================
def pick_top_similar_reviews(product, customer, profile, top_k=10):
    reviews = product.get("reviews", [])
    forbidden_terms = ["🤍🤍🤍"]
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

    # 점수 + 평점 순 정렬
    ranked = sorted(
        scored,
        key=lambda x: (x["score"], x["rating"]),
        reverse=True
    )

    selected = []
    seen_keys = set()   # 중복 검사용

    for item in ranked:
        review = item["review"]

        text_norm = _normalize_text(review.get("review_text"))

        # 🚫 금지어 포함 리뷰 제외
        if any(term.lower() in text_norm for term in map(str.lower, forbidden_terms)):
            continue

        # 🔁 중복 제거
        # review_id 우선 기준
        key = review.get("review_id") or text_norm
        if key in seen_keys:
            continue
        seen_keys.add(key)
        selected.append(review)

        # ▶️ K개 채워지면 종료
        if len(selected) >= top_k:
            break

    return selected

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
    USER_ID = "U005"

    reco, customer, profile = recommend_products(USER_ID)
    context = build_rag_context(reco)

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

    message = generate_marketing_message(context, customer)

    print("\n=== 📨 생성된 CRM 개인화 메시지 ===\n")
    print(message)
