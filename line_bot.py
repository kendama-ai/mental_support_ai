from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from services import get_next_question, get_result
import os

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

user_states = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    state = user_states.get(user_id, {"step": 1})
    step = state.get("step", 1)

    # ===== フロー処理 =====
    if step == 1:
        state["category"] = text
        state["history"] = [text]
        state["step"] = 2

    elif step == 2:
        state["status"] = text
        state["history"].append(text)
        state["step"] = 3

    elif step == 3:
        state["income"] = text
        state["history"].append(text)

        result = get_result(state)
        user_states.pop(user_id, None)

        # ===== 結果表示 =====
        messages = []

        messages.append(TextSendMessage(
            text=f"【{result['name']}】\n\n{result['description']}"
        ))

        if result.get("map_url"):
            messages.append(TextSendMessage(
                text=f"📍 地図\n{result['map_url']}"
            ))

        if result.get("tel"):
            messages.append(TextSendMessage(
                text=f"📞 電話\n{result['tel']}"
            ))

        line_bot_api.reply_message(event.reply_token, messages)
        return  # ←ここ重要

    # ===== 質問表示（step1,2） =====
    user_states[user_id] = state

    next_q = get_next_question(state)

    quick_reply = QuickReply(items=[
        QuickReplyButton(action=MessageAction(label=o, text=o))
        for o in next_q["options"]
    ])

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=next_q["question"],
            quick_reply=quick_reply
        )
    )