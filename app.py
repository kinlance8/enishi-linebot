from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

DATA_FILE = "user_access_log.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def is_user_allowed(user_id):
    data = load_user_data()
    now = datetime.now()
    month_key = now.strftime("%Y-%m")
    if user_id in data and data[user_id] == month_key:
        return False
    data[user_id] = month_key
    save_user_data(data)
    return True

def log_to_sheets(user_id, message):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL')}"
    }
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([user_id, timestamp, message])

advice_list = [
    "あなたの気持ち、ちゃんと届こうとしていますよ。焦らず、自分を信じてあげてくださいね。",
    "この道に“正解”なんてなくていいんです。あなたのペースが、いちばん大切です。",
    "がんばった分、あなた自身にも優しさを返してあげてください。",
    "“大切にされたい”って思っていいんです。まずは自分を大切にしてあげましょう。",
    "誰かの言葉がすべてじゃありません。未来は、あなたの手で描けます。",
    "不安を感じるのは自然なこと。がんばって笑わなくても、大丈夫ですよ。",
    "不器用でも大丈夫。そんなあなたを好きになる人が、きっといます。",
    "“選ばれるか”じゃなくて、自分が心地いいかどうか。それが一番大事な軸です。",
    "“わかってほしい”って気持ちも、あなたが誰かを受け入れる準備かもしれません。",
    "迷ったときは、“安心できるほう”を選んでくださいね。心がちゃんと知っています。",
    "あなたの価値は、恋愛や誰かの反応で決まるものじゃないんです。",
    "誰かを変えようとするより、自分の軸を整えてみると、景色が変わりますよ。",
    "もし今、何かが終わりかけているなら、それは新しい何かのはじまりです。",
    "願いが叶わない時、それはもっと良い方向に進むチャンスかもしれません。",
    "“手放す”ことは、決して諦めではなく、新しいものを迎えるための準備なんです。",
    "真剣に向き合っているあなたの姿、ちゃんと見てくれている人がいますよ。",
    "“大丈夫”って言えない日があってもいいんです。ゆっくりで、大丈夫。",
    "ひとつ動くだけで、未来の景色はきっと変わり始めます。",
    "迷いの中にいるときこそ、心の声をじっくり聞いてあげてください。",
    "言葉や態度より、“感じたこと”を信じてみてください。それが本当の答えかも。",
    "“待つ”という時間も、大切な愛の育ち方のひとつです。",
    "うまく言えなくても、あなたの想いは、ちゃんと伝わっていますよ。",
    "縁がある人とは、自然と繋がれます。焦らなくていいんです。",
    "焦る気持ちは手放して、“信じる”という力をそっと育てていきましょう。",
    "理由はなくても、“なんとなく”感じたことは、案外あたっていたりします。",
    "あなたの笑顔が、気づかぬうちに誰かの支えになっています。",
    "もうダメだ…そんなふうに思った先に、本当のスタートが待っているかもしれません。",
    "その“傷ついた経験”は、いつか誰かの救いになる言葉に変わります。",
    "どんなにしんどい今日でも、明日はまっさらな白紙。何度でも描き直せます。",
    "どんな未来でも、あなたには“選び直す力”がちゃんとあるんです。"
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
    user_id = event.source.user_id

    if "縁カードで占って" in user_input:
        if is_user_allowed(user_id):
            advice = random.choice(advice_list)
            message = (
                "🪄✨今月のあなたに贈る、ひとことメッセージ🐈‍⬛\n\n"
                f"{advice}\n\n"
                "ふと心に響いたら、それは“運命のサイン”かもしれません。\n\n"
                "🌙この言葉の意味がもっと知りたいあなたへ。\n\n"
                "今のあなたに必要な\n"
                "“縁のメッセージ”を、\n"
                "鑑定で丁寧にお届けします。\n\n"
                "💫願いをそっと後押しする\n"
                "【縁カード】（幸運招来エネルギー封入ver.）も\n"
                "数量限定でご用意しています🐾✨\n\n"
                "▶︎ LINEメニューの【SHOP】からご覧ください🔮"
            )
        else:
            message = (
                "🔒 月1回限定・縁カードメッセージ【占い使用済み時の返信】\n\n"
                "⚠️この占いは【月に一度だけ】の特別なメッセージです🌙\n\n"
                "今月はもうご利用済みのようですね💌\n"
                "でも、落ち込まないでください。\n\n"
                "お願いを叶える【縁カード】は、\n"
                "“幸運招来エネルギー”を込めた特別な1枚🐾✨\n\n"
                "あなたの願いが動き出すタイミングを、いつでもサポートしています。\n\n"
                "🔮鑑定＆カード購入はLINEメニュー【SHOP】からご確認ください🐈‍⬛"
            )

        log_to_sheets(user_id, user_input)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
