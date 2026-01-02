import os
import json
from api_and_path import *

# =========================
# 공용 로더
# =========================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_product(pid):
    return load_json(os.path.join(PRODUCT_DIR, f"{pid}.json"))


def load_customer(uid):
    return load_json(os.path.join(CUSTOMER_DIR, f"{uid}.json"))


def load_brands():
    return {b["brand_id"]: b for b in load_json(BRAND_DB)}