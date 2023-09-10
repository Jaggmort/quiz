import os
import logging

import dotenv
import telegram

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram_log import TelegramLogsHandler
from txt_questions import get_questions

logger = logging.getLogger(__name__)


def answer(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    qst = get_questions('questions\\osel95.txt')
    qst[1]['question']
    if update.message.text=='Новый вопрос':
        update.message.reply_markdown_v2(
            'test',
            reply_markup=reply_markup,
        )
    else:

        update.message.reply_text(
            qst[1]['question']
        )


def main() -> None:
    dotenv.load_dotenv('.env')
    tg_token = os.environ['TELEGRAM_TOKEN']
    tg_announce_token = os.environ['TG_ANNOUNCE_TOKEN']
    tg_announce_bot = telegram.Bot(tg_announce_token)
    tg_announce_id = os.environ['TELEGRAM_USER_ID']

    logger_settings = TelegramLogsHandler(tg_announce_bot, tg_announce_id)
    logger_settings.setLevel(logging.INFO)
    logger_settings.setFormatter(
        logging.Formatter("%(asctime)s: %(levelname)s; %(message)s")
        )
    logger.addHandler(logger_settings)

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, answer)
        )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
