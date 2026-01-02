import math
from loader import *

# =========================
# ✦ 동적 가중치 (피부특징 제거)
#  → 총 6개 특징, 합 = 1
# =========================
def compute_dynamic_feature_weights(num_purchases):

    progress = min(1.0, num_purchases / 20.0)
    decay = math.exp(-3 * progress)

    weights = {
        # 초기 데이터 부족 → 행동 기반 의존
        "pick_similarity": (1/2) * decay + (1/6) * (1 - decay),
        "basket_similarity": (1/2) * decay + (1/6) * (1 - decay),

        # 구매 데이터 충분 → 점차 균등화
        "price_match": (0) * decay + (1/6) * (1 - decay),
        "discount_match": (0) * decay + (1/6) * (1 - decay),
        "category_match": (0) * decay + (1/6) * (1 - decay),
        "planning_match": (0) * decay + (1/6) * (1 - decay),
    }

    total = sum(weights.values())
    for k in weights:
        weights[k] /= total

    return weights

# =========================
# ✦ 찜/장바구니 유사도
# =========================
def compute_similarity_against_set(product, id_list):
    if not id_list:
        return 0.0

    target_tags = set(product.get("tags", []))
    sims = []

    for pid in id_list:
        try:
            p = load_product(pid)
        except:
            continue

        tags = set(p.get("tags", []))
        if not tags:
            continue

        jaccard = len(target_tags & tags) / len(target_tags | tags)
        sims.append(jaccard)

    return max(sims) if sims else 0.0

# =========================
# ✦ 리뷰 친화도 점수 계산(평균 별점)
# =========================
def compute_review_affinity_avg(product):
    reviews = product.get("reviews", [])
    if not reviews:
        return 0

    avg = sum(r["overall_rating"] for r in reviews) / len(reviews)
    return avg / 5.0

# =========================
# 제품 매칭 점수 계산
#  (6개 특징 + 리뷰 1)
# =========================
def compute_product_match_score(product, customer, profile):

    weights = compute_dynamic_feature_weights(profile["num_purchases"])
    details = {"weights": weights}
    score_sum = 0

    # --- 찜 유사도 ---
    pick_sim = compute_similarity_against_set(product, profile["pick_list"])
    details["pick_similarity"] = {
        "score": round(pick_sim, 3),
        "weight": round(weights["pick_similarity"], 3)
    }
    score_sum += pick_sim * weights["pick_similarity"]

    # --- 장바구니 유사도 ---
    basket_sim = compute_similarity_against_set(product, profile["basket"])
    details["basket_similarity"] = {
        "score": round(basket_sim, 3),
        "weight": round(weights["basket_similarity"], 3)
    }
    score_sum += basket_sim * weights["basket_similarity"]

    # --- 가격 ---
    price_gap = abs(product["price_current"] - profile["avg_price_paid"])
    price_score = max(0, 1 - price_gap / max(1, profile["avg_price_paid"]))
    details["price_match"] = {
        "score": round(price_score, 3),
        "weight": round(weights["price_match"], 3)
    }
    score_sum += price_score * weights["price_match"]

    # --- 할인 ---
    discount_gap = abs(product["discount_rate"] - profile["avg_discount_rate"])
    discount_score = max(0, 1 - discount_gap)
    details["discount_match"] = {
        "score": round(discount_score, 3),
        "weight": round(weights["discount_match"], 3)
    }
    score_sum += discount_score * weights["discount_match"]

    # --- 카테고리 ---
    raw = 0
    for t in product.get("tags", []):
        raw += profile["category_pref"].get(t, 0)
    cat_score = math.log(raw + 1)
    details["category_match"] = {
        "score": round(cat_score, 3),
        "weight": round(weights["category_match"], 3)
    }
    score_sum += cat_score * weights["category_match"]

    # --- 기획상품 선호 ---
    planning_pref = profile["planning_liking"]
    planning_score = 1.0 if product["is_planning_product"] else 0.5 * planning_pref
    details["planning_match"] = {
        "score": round(planning_score, 3),
        "weight": round(weights["planning_match"], 3)
    }
    score_sum += planning_score * weights["planning_match"]

    # ✦ 리뷰 점수 (=1 스케일)
    review_score = compute_review_affinity_avg(product)

    details["review_affinity"] = {
        "score": round(review_score, 3),
        "weight": 1.0,
    }

    final_score = score_sum + review_score

    details["feature_score"] = round(score_sum, 4)
    details["final_score"] = round(final_score, 4)

    return final_score, details