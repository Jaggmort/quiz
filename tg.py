import os
import logging
import random

import dotenv
import redis
import telegram

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram_log import TelegramLogsHandler


logger = logging.getLogger(__name__)

TG_BOT_KEYBOARD = [['Новый вопрос', 'Сдаться']]
CHOOSING, TYPING_ANSWER = range(2)


def start(update, _):
    update.message.reply_text(
        'Здравствуйте, это бот для проведение викторины.',
        reply_markup=ReplyKeyboardMarkup(TG_BOT_KEYBOARD),
    )
    return CHOOSING


def handle_new_question_request(update, _, storage):
    questions = storage.hgetall('questions')
    message = random.choice(list(questions))
    storage.mset({str(update.effective_user.id): message})
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(TG_BOT_KEYBOARD),
    )
    return TYPING_ANSWER


def handle_solution_attempt(update, _, storage):
    questions = storage.hgetall('questions')
    short_correct_answer = questions[storage.get(str(update.effective_user.id))].\
        split('.', 1)[0].replace('"', '')
    if update.message.text.lower() in short_correct_answer.lower():
        message = 'Все верно! Для следующего вопроса нажми «Новый вопрос»'
        return_params = CHOOSING
    else:
        message = 'Неправильно… Ещё одна попытка?'
        return_params = TYPING_ANSWER
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(TG_BOT_KEYBOARD, resize_keyboard=True),
    )
    return return_params


def handle_give_up(update, _, storage):
    questions = storage.hgetall('questions')
    short_correct_answer = questions[storage.get(str(update.effective_user.id))]. \
        split('.', 1)[0].replace('"', '')
    update.message.reply_text(short_correct_answer)
    handle_new_question_request(update, _, storage)
    return TYPING_ANSWER


def cancel(update, _):
    print('tt')
    user = update.message.from_user
    logger.info(f'User {user.first_name} canceled the conversation.')
    update.message.reply_text('До свидания! Ждем вас снова.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def _error(update, _error):
    logger.warning(f'Update {update} caused error {_error}')


def main() -> None:
    dotenv.load_dotenv('.env')
    tg_token = os.environ['TELEGRAM_TOKEN']
    tg_announce_token = os.environ['TG_ANNOUNCE_TOKEN']
    tg_announce_id = os.environ['TELEGRAM_USER_ID']
    tg_announce_bot = telegram.Bot(tg_announce_token)
    storage = redis.Redis(
        host=os.environ.get('REDIS_HOST', default='localhost'),
        port=os.environ.get('REDIS_PORT', default=6379),
        password=os.environ.get('REDIS_PASSWORD', default=''),
        db=os.environ.get('REDIS_DB', default=0),
        decode_responses=True
    )

    logger_settings = TelegramLogsHandler(tg_announce_bot, tg_announce_id)
    logger_settings.setLevel(logging.INFO)
    logger_settings.setFormatter(
        logging.Formatter("%(asctime)s: %(levelname)s; %(message)s")
        )
    logger.addHandler(logger_settings)

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Новый вопрос$'),
                                      lambda update, _: handle_new_question_request(update, _, storage)
                                      ),
                       ],
            TYPING_ANSWER: [MessageHandler(Filters.regex('^Сдаться$'),
                                           lambda update, _: handle_give_up(update, _, storage)),
                            MessageHandler(Filters.text & (~ Filters.command),
                                           lambda update, _: handle_solution_attempt(update, _, storage),
                                           pass_user_data=True),
                            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(_error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
