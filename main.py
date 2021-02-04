from telegram.ext import Updater, CommandHandler, PollHandler, PollAnswerHandler, CallbackQueryHandler, MessageHandler, \
    Filters
from modules.functions import welcome, help_menu
from modules.handlers import callback_query_handler, message_handler, poll_handler, poll_answer_handler
import os
import data

if __name__ == '__main__':
    updater = Updater('1429135380:AAGeHjnn8aoWK-nr3NZon3UT4RFE12PkhXw', use_context=True)
    dp = updater.dispatcher

    if os.path.isfile('current_list'):
        data.deserialize()

    dp.add_handler(CommandHandler('start', help_menu))
    # dp.add_handler(CommandHandler('menu', start))
    dp.add_handler(CommandHandler('help', help_menu))
    dp.add_handler(CommandHandler('chat', help_menu))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    dp.add_handler(MessageHandler(Filters.text, message_handler))
    dp.add_handler(PollHandler(poll_handler))
    dp.add_handler(PollAnswerHandler(poll_answer_handler))

    updater.start_polling()
    updater.idle()
