from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random
import json
from datetime import datetime

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# ファイルにユーザー使用記録を保存
DATA_FILE = "user_access_log.json"

# 占いの使用履歴を読み込み
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# 占い使用履歴を保存
def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# 月1回制限をチェック
def is_user_allowed(user_id):
    data = load_user_data()
    now = datetime.now()
    month_key = now.strftime("%Y-%m")

    if user_id in data and data[user_id] == month_key:
        return False
    data[user_id] = month_key
    save_user_data(data)
    return True

# 使用ログの記録（オプション）
LOG_FILE = "usage_log.txt"
def log_usage(user_id, message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{now},{user_id},{message}\n")

# LINEのWebhook受け取りルート
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")
        return "NG", 400

    return "OK", 200

# 占い応答メッセージ
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id

    if "縁カードで占って" in user_input:
        if is_user_allowed(user_id):
            advice_list = [
                "あなたの気持ちは、届く準備ができています。",
                "行動に移すことで、未来は変わり始めます。",
                "“大丈夫”と笑える日は、もう少し先でもきっと来るから。",
                "願いが叶わない時こそ、軌道修正のチャンスかもしれません。"
            ]
            advice = random.choice(advice_list)
            message = (
                f"🪄✨今月のあなたへのひとこと🐈‍⬛\n\n"
                f"{advice}\n\n"
                f"🐾この言葉の意味が気になる方は\n"
                f"LINEメニューのSHOPから鑑定をお申し込みくださいね🌙\n\n"
                f"💫さらに願いを後押ししたい方へ\n"
                f"願いが叶う【縁カード】（幸運招来エネルギー封入ver.）は数量限定で販売中✨\n"
                f"▶︎ 鑑定・ご購入はLINEメニューの【SHOP】から🔮"
            )
        else:
            message = (
                "🪄すでに今月の占いは受け取られています✨\n"
                "来月までお楽しみに…🌙\n\n"
                "▶ 鑑定をご希望の方はLINEメニューの【SHOP】からどうぞ🔮"
            )

        log_usage(user_id, user_input)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
