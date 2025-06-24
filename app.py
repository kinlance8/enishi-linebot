from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Googleスプレッドシート連携の設定
def get_gspread_client():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict({
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL")
    }, scope)
    return gspread.authorize(credentials)

# 使用履歴をGoogle Sheetsで管理（月1制限）
def is_user_allowed(user_id):
    client = get_gspread_client()
    sheet = client.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1
    records = sheet.get_all_records()

    current_month = datetime.now().strftime("%Y-%m")

    for record in records:
        if record['user_id'] == user_id and record['month'] == current_month:
            return False

    sheet.append_row([user_id, current_month])
    return True

# 占いメッセージ
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()
    user_id = event.source.user_id

    if user_input == "縁カードで占って":
        if is_user_allowed(user_id):
            advice = random.choice(advice_list)
            reply = f"🪄✨今月のあなたに贈る、ひとことメッセージ🐈‍⬛\n\n{advice}\n\nふと心に響いたら、それは“運命のサイン”かもしれません。\n\n🌙この言葉の意味がもっと知りたいあなたへ。\n\n今のあなたに必要な“縁のメッセージ”を、鑑定で丁寧にお届けします。\n\n💫願いをそっと後押しする【縁カード】（幸運招来エネルギー封入ver.）も数量限定でご用意しています🐾✨\n\n▶︎ LINEメニューの【SHOP】からご覧ください🔮"
        else:
            reply = "⚠️この占いは【月に一度だけ】の特別なメッセージです🌙\n\n今月はもうご利用済みのようですね💌でも、落ち込まないでください。\n\nお願いを叶える【縁カード】は、“幸運招来エネルギー”込めた特別な1枚🐾✨\n\nあなたの願いが動き出すタイミングを、いつでもサポートしています。\n\n🔮鑑定＆カード購入はLINEメニュー【SHOP】からご確認ください🐈‍⬛"

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return "OK", 200

if __name__ == "__main__":
    app.run()
