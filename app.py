from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 厳選30個の刺さるひとこと（自由に増減OK）
advice_list = [
    "あなたの気持ちは、届く準備ができています。焦らず信じて。",
    "恋の進み方に、正解なんてありません。あなたのペースで大丈夫。",
    "愛されたいと思う日こそ、自分に優しくしてあげて。",
    "“大切にされたい”と思ったとき、それはあなた自身から始まります。",
    "恋の迷いは、あなたの心が真剣だからこそ。",
    "無理に繋がるよりも、自然に寄り添えるご縁を。",
    "不安があるのは、ちゃんと好きな証拠です。",
    "相手を変えようとする前に、自分を大切にすることから。",
    "愛は、追いかけるより“迎え入れる”ものです。",
    "その恋に傷ついたのは、あなたが本気だった証。",
    "わかり合えないのではなく、まだ見えていないだけかもしれません。",
    "優しくできない日は、自分を守る日だったと思って。",
    "無理に分かってもらわなくていい。あなたの心を守ることが先。",
    "気をつかいすぎた心には、静かな時間が必要です。",
    "距離を置くことも、立派なやさしさのひとつ。",
    "苦手な人は、“あなたの内側”を映す鏡かもしれません。",
    "疲れる関係は、もう卒業のサインかもしれない。",
    "本音を言えない関係より、黙っていられる関係を大切に。",
    "お金は“心のゆとり”の流れに乗ってやってきます。",
    "惜しみなく与えられる人のもとに、豊かさは巡ります。",
    "不安から使うお金は、不安を連れて戻ってきます。",
    "豊かさは、安心の中に生まれます。自分を信じて使ってみて。",
    "頑張りすぎているあなたへ。少し立ち止まっても、大丈夫。",
    "比べることをやめたとき、本当の魅力が開きはじめます。",
    "今はまだ整える時期。焦らず、根を伸ばして。",
    "今の違和感は、次のステージの合図です。",
    "あなたの涙は、心の浄化。その後には光が見えます。",
    "思い通りにならない日も、未来への種まきです。",
    "今日うまくいかないのは、明日を整えてくれているから。",
    "何も動けない時期も、大切な“成長の仕込み時間”です。"
]

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)
        return "NG", 400
    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()

    if user_input == "縁カードで占って":
        advice = random.choice(advice_list)

        full_message = f"""🪄 今月のあなたへのひとことメッセージ 🐈‍⬛

「{advice}」

🐾この言葉の意味が気になる方は、LINEメニューのSHOPから鑑定をお申し込みくださいね🌙"""

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=full_message)
        )
