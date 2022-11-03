import logging
from pprint import pprint
import random

from sdam_gia import SdamGIA

from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
SUBJECT = 'inf'


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Вариант", callback_data="variant"),
            InlineKeyboardButton("Задачи", callback_data="zadacha"),
        ]
    ]
    keyboard_markup = InlineKeyboardMarkup(keyboard)

    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.full_name}!\n"
        f"Это бот для подготовки к ОГЭ по информатике.\n"
        f"Чтобы начать решение варианта нажми на кнопку Вариант.\n"
        f"Чтобы начать решать случайные задачи нажми на Задачи.\n",
        reply_markup=keyboard_markup,
    )


def button(update: Update, context: CallbackContext):
    # обработка кнопок
    query = update.callback_query
    callbackdata = query.data

    if callbackdata == "variant":
        print("вы тыкнули на кнопку вариант")
    elif callbackdata == "zadacha":
        keyboard = [
            [
                InlineKeyboardButton("1", callback_data="z1"),
                InlineKeyboardButton("2", callback_data="z2"),
                InlineKeyboardButton("3", callback_data="z3")
            ],
            [
                InlineKeyboardButton("4", callback_data="z4"),
                InlineKeyboardButton("5", callback_data="z5"),
                InlineKeyboardButton("6", callback_data="z6"),
            ],
            [

                InlineKeyboardButton("7", callback_data="z7"),
                InlineKeyboardButton("8", callback_data="z8"),
                InlineKeyboardButton("9", callback_data="z9"),
            ],
            [
                InlineKeyboardButton("10", callback_data="z10"),
                InlineKeyboardButton("11", callback_data="z11"),
                InlineKeyboardButton("12", callback_data="z12"),
            ]
        ]
        keyboard_markup = InlineKeyboardMarkup(keyboard)
        sdamgia = SdamGIA()
        catalog = sdamgia.get_catalog(SUBJECT)
        message = "Выберите номер задачи.\n"
        for i, topic in enumerate(catalog):
            message += f"{i + 1} - {topic['topic_name']}\n"
        query.edit_message_text(
            text=message,
            reply_markup=keyboard_markup
        )
    elif callbackdata.startswith('z'):
        # Из кода кнопки получаем номер
        topic_index = int(callbackdata[1:])
        # Получаем список тем
        sdamgia = SdamGIA()
        catalog = sdamgia.get_catalog(SUBJECT)
        # Получение всех задач темы
        tasks = sdamgia.get_category_by_id(SUBJECT, catalog[topic_index]['topic_id'])
        # Выбор случайной задачи
        task = sdamgia.get_problem_by_id(SUBJECT, tasks[random.randint(0, len(tasks))])

        pprint(task)

        message = f"Задача {task['id']}\n" + f"{task['condition']['text']}\n"
        keyboard = [
            [
                InlineKeyboardButton("Cледующая задача", callback_data=f"z{topic_index}"),
            ]
        ]
        keyboard_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text=message,
            reply_markup=keyboard_markup
        )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("5473975984:AAGAWJKsgRG3jcI3Rb1878ePlRoEZnDkoaI")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CallbackQueryHandler(button))
    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
