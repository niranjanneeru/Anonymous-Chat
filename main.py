import os

from telegram.ext import (Updater, CommandHandler, PollHandler, PollAnswerHandler, CallbackQueryHandler, MessageHandler,
                          Filters)

import data
from database.db import Db
from modules.functions import help_menu, status, skip
from modules.handlers import (callback_query_handler, message_handler, poll_handler, poll_answer_handler,
                              sticker_handler, message_all_handler)
from modules.admin_commands import store

from modules.questionnaire import cancel

if __name__ == '__main__':
    updater = Updater('1429135380:AAGeHjnn8aoWK-nr3NZon3UT4RFE12PkhXw', use_context=True)
    dp = updater.dispatcher

    if os.path.isfile('current_list'):
        data.deserialize()

    dp.add_handler(CommandHandler('start', help_menu))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(CommandHandler('menu', store))
    dp.add_handler(CommandHandler('help', help_menu))
    dp.add_handler(CommandHandler('chat', help_menu))
    dp.add_handler(CommandHandler('cancel', cancel))
    dp.add_handler(CommandHandler('skip', skip))
    dp.add_handler(CallbackQueryHandler(callback_query_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
    dp.add_handler(MessageHandler(Filters.sticker, sticker_handler))
    dp.add_handler(MessageHandler(Filters.all, message_all_handler))
    dp.add_handler(PollHandler(poll_handler))
    dp.add_handler(PollAnswerHandler(poll_answer_handler))

    Db.get_instance().create_black_list()
    Db.get_instance().create_active_command_list()

    updater.start_polling()
    updater.idle()
