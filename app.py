from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 🐈‍⬛ 厳選30個のひとこと（自由に増減OK）
advice_list = [
    "あなたの気持ちは、届く準備ができています。焦らず信じて。",
    "この流れに、正解なんてありません。あなたのペースで大丈夫。",
    "受け止めるときこそ、自分に優しくしてあげて。",
    "大切にされたいと思えたこと。それはあなた自身から始まります。",
    "運命は、あなたの決断から動き出す。",
    "自分を許せるとき、目の前に優しさが返ってくる道標。",
    "不安があるのは、ちゃんと好きな証拠です。",
    "誰かを信じるという選択、自分を信じてすることから。",
    "感情に蓋をしないで。出し切ることが、受け入れる準備。",
    "距離をとる勇気が、ふたりの未来を近づけることもあります。",
    "心の声を無視しないで。小さな違和感は本音の合図。",
    "今は“待つ”ことで、動き出す未来があります。",
    "寂しさに優しさをくっつけて、自分にそっと与えてあげて。",
    "恋愛は駆け引きじゃなく、タイミングの重なり。",
    "あなたの価値は、誰かの態度で決まるものじゃない。",
    "願うだけじゃなく、叶う前提で行動してみて。",
    "今、目の前にある“違和感”が新しい道のヒントになるかも。",
    "“終わること”は新しい始まりの準備だったりします。",
    "諦めるのは、負けじゃなく“選びなおす勇気”。",
    "運命は偶然じゃなく、“選んだ結果”の連続です。",
    "頑張りすぎた自分を、ちゃんと認めてあげて。",
    "あなたの直感は、思っているより正確です。",
    "何もない日は、心を整えるギフトの時間。",
    "恋愛に正解はないけれど、“後悔しない選択”はできる。",
    "愛されたいと思う前に、自分を大切にしてあげよう。",
    "あなたの価値は、恋愛の結果では決まりません。",
    "過去にとらわれすぎないで。今のあなたが一番新しい。",
    "ちゃんと気づいてるよ。あなたは本当によくやってる。",
    "誰かの言葉じゃなく、自分の声を信じて。",
    "心配しすぎるより、“信じる覚悟”を持ってみて。"
]

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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()

    if "縁カードで占って" in user_input:
        selected_advice = random.choice(advice_list)
        message = (
            f"🪄今日のあなたへのひとこと🐈‍⬛\n\n"
            f"{selected_advice}\n\n"
            f"🐾この言葉の意味が気になる方はLINEメニューのSHOPから鑑定をお申し込みくださいね🌙"
        )
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )
