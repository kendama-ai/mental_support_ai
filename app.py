# app.py
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = "secret"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def get_next_question(state):
    step = state.get("step", 1)

    if step == 1:
        return {
            "question": "お住まいの地域を選んでください",
            "options": ["川口市", "さいたま市", "その他"]
    }

    elif step == 2:
        return {
            "question": "今つらいことは？",
            "options": ["働けない", "休職中", "お金に困っている", "通院している"]
        }

    elif step == 3:
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

    elif step == 4:
        return {
            "question": "収入はありますか？",
            "options": ["ある", "ない"]
        }

    # 🔥 これ追加（重要）
    return {
        "question": "最初に戻ります",
        "options": ["働けない", "休職中"]
    }

def get_result(state):
    category = state.get("category")
    income = state.get("income")

    if category == "働けない":
        if income == "ない":
            return {
                "name": "生活保護",
                "description": "市役所に相談してください",
                "map_url": "https://maps.google.com/?q=市役所"
            }
        else:
            return {
                "name": "失業手当",
                "description": "ハローワークで手続き",
                "map_url": "https://maps.google.com/?q=ハローワーク"
            }

    elif category == "休職中":
        return {
            "name": "傷病手当金",
            "description": "会社または健康保険組合に申請してください",
            "map_url": "https://maps.google.com/?q=会社"
        }

    elif category == "お金に困っている":
        return {
            "name": "生活保護",
            "description": "市役所に相談してください",
            "map_url": "https://maps.google.com/?q=市役所"
        }

    elif category == "通院している":
        return {
            "name": "自立支援医療",
            "description": "医療費の負担が軽減されます",
            "map_url": "https://maps.google.com/?q=市役所"
        }

    # 🔥 最重要（絶対入れる）
    return {
        "name": "相談窓口",
        "description": "状況を詳しく確認する必要があります",
    }

@app.route("/")
def index():
    session.clear()
    session["state"] = {"step": 1}
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    state = session.get("state", {"step": 1})

    step = state.get("step", 1)

    if step == 1:
        state["city"] = user_input
        state["history"] = [user_input]
        state["step"] = 2

    elif step == 2:
        state["category"] = user_input
        state["history"].append(user_input)
        state["step"] = 3

    elif step == 3:
        state["status"] = user_input
        state["history"].append(user_input)
        state["step"] = 4

    elif step == 4:
        state["income"] = user_input
        state["history"].append(user_input)

        result = get_result(state)
        session.clear()

        return jsonify({
            "result": result,
            "history": state["history"]
        })
    # 次の質問
    session["state"] = state
    next_q = get_next_question(state)

    return jsonify({
        "question": next_q["question"],
        "options": next_q["options"],
        "history": state.get("history", [])
    })

from line_bot import handler
from linebot.exceptions import InvalidSignatureError

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "error", 400

    return "OK"

@app.route("/back", methods=["POST"])
def back():
    state = session.get("state", {"step": 1})

    step = state.get("step", 1)

    if step > 1:
        state["step"] = step - 1

        # 🔥 履歴も戻す
        if "history" in state and state["history"]:
            state["history"].pop()

    session["state"] = state

    next_q = get_next_question(state)

    return jsonify({
        "question": next_q["question"],
        "options": next_q["options"],
        "history": state.get("history", [])
    })

if __name__ == "__main__":
    app.run(debug=True)