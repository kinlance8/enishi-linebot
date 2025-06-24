@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text.strip()

    if "縁カードで占って" in user_input:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="縁カードの神託を受け取りました🔮")
        )
