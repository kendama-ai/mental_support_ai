# services.py
import json

# ===== DB読み込み =====
with open("data/zip.json", encoding="utf-8") as f:
    ZIP_DB = json.load(f)

with open("data/services.json", encoding="utf-8") as f:
    SERVICES_DB = json.load(f)

with open("data/cities.json", encoding="utf-8") as f:
    CITY_DB = json.load(f)


# ===== 郵便番号 =====
def get_city_from_zip(zip_code):
    return ZIP_DB.get(zip_code, "その他")


# ===== スコアリング =====
def match_score(service, state):
    score = 0
    conditions = service.get("conditions", {})

    for key, value in conditions.items():
        if state.get(key) == value:
            score += 50
        else:
            return 0

    score += service.get("score", 0)
    return score


# ===== 会話フロー =====
def get_next_question(state):
    step = state.get("step", 1)

    if step == 1:
        return {
            "question": "今つらいことは？",
            "options": ["働けない", "休職中", "お金に困っている", "通院している"]
        }

    elif step == 2:
        if state.get("category") == "働けない":
            return {
                "question": "現在の状況は？",
                "options": ["退職している", "休職中", "未経験"]
            }
        elif state.get("category") == "休職中":
            return {
                "question": "どのくらい休んでいますか？",
                "options": ["1ヶ月未満", "1ヶ月以上"]
            }

    elif step == 3:
        return {
            "question": "収入はありますか？",
            "options": ["ある", "ない"]
        }

    return {
        "question": "最初に戻ります",
        "options": ["働けない", "休職中"]
    }


# ===== 結果ロジック =====
def get_result(state):
    city = state.get("city")

    # 郵便番号補完
    if not city and state.get("zip"):
        city = get_city_from_zip(state["zip"])

    best_service = None
    best_score = 0

    for service in SERVICES_DB:
        score = match_score(service, state)

        if score > best_score:
            best_score = score
            best_service = service

    # fallback
    if not best_service:
        return {
            "name": "相談窓口",
            "description": "お住まいの自治体に相談してください"
        }

    # 地域情報
    city_info = CITY_DB.get(city, {})
    dept = city_info.get("departments", {}).get(
        best_service.get("department"), {}
    )

    return {
        "name": best_service["name"],
        "description": f"{dept.get('name', '')}に相談してください",
        "tel": dept.get("tel"),
        "map_url": dept.get("map")
    }