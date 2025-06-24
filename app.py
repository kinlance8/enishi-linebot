from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# 👤 ユーザーごとの前回メッセージ記録（再起動でリセットされます）
user_last_result = {}

# 🌟 今月のひとことリスト（30個）
advice_list = [
    "あなたの気持ちは、届く準備ができています。焦らず信じて。",
    "この道の先に、正解なんてありません。あなたのペースで大丈夫。",
    "突き進んだと思うこと、自分にも優しくしてあげて。",
    "“大切にされたい”と思ったこと。それはあなた自身から始まります。",
    "誰かの言葉は、あなたの未来を縛ることはできません。",
    "不安を抱えるのも、自然な流れ。無理に笑わなくて大丈夫。",
    "不器用なあなたは、ちゃんと好かれる魅力を持っている。",
    "“選ばれるか”ではなく、自分を心地よくすることから。",
    "“理解されたい”と思う心も、受け入れる準備の一歩。",
    "もし何かに迷ったら、“安心できる選択”を大切に。",
    "あなたの価値は、恋愛の結果では決まりません。",
    "一緒にいる人を変えるのではなく、自分の軸を強くしてみて。",
    "今、何かが終わろうとしているなら、それは始まりのサイン。",
    "願いが叶わない時こそ、軌道修正のチャンスかもしれません。",
    "“手放す”勇気が、“入ってくる”余白を作ります。",
    "ちゃんと向き合っているあなたを、誰かは見てくれています。",
    "“大丈夫”と笑える日は、もう少し先でもきっと来るから。",
    "行動に移すことで、未来は変わり始めます。",
    "迷った時ほど、心の声を聞いてみてください。",
    "言葉より、態度より、感覚を信じてみてもいい。",
    "“待つ”ことで愛が育つこともある。",
    "うまく話せないあなたでも、ちゃんと伝わっている。",
    "タイミングの合わない人とは、無理に繋がらなくていい。",
    "焦りは手放して、“信じる力”を育てていきましょう。",
    "“なんとなく”を信じる日があってもいい。",
    "あなたが笑ってることが、周りを救っている。",
    "もうダメだと思ってからが、始まりの合図。",
    "“傷ついた経験”が、誰かを救う言葉に変わる日がきます。",
    "たとえ今日が苦しくても、明日はまだ白紙です。",
    "どんな未来でも、あなたには選び直す力がある。"
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
    user_id = event.source.user_id
    user_input = event.message.text.strip()

    if "縁カードで占って" in user_input:
        # 前回と同じアドバイスを避ける
        max_attempts = 5
        for _ in range(max_attempts):
            idx = random.randint(0, len(advice_list) - 1)
            if user_last_result.get(user_id) != idx:
                break
        user_last_result[user_id] = idx

        message = (
            "🪄✨今月のあなたへのひとこと🐈‍⬛\n\n"
            + advice_list[idx]
            + "\n\n🐾この言葉の意味が気になる方はLINEメニューのSHOPから鑑定をお申し込みくださいね🌙"
        )

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )

if __name__ == "__main__":
    app.run()
