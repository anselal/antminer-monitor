import traceback

import requests

from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def notify_telegram(message: str):
    """
    Sends a message to a Telegram chat using the Telegram Bot API.

    Args:
        message (str): The message to send.

    Raises:
        Exception: If there was an error while sending the message.

    Returns:
        None: This function does not return anything.

    Example:
        To send a message to a Telegram chat:
        ```
        notify_telegram("Hello, world!")
        ```
    """
    try:
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID and message:
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
            }
            requests.post(
                url=
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                data=payload)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
