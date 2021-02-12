from telegram import Update
from telegram.ext import CallbackContext
from database.db import Db
from data import serialize, active_chats, current_list_users, active_commands, active_requests
from utils import (ADMIN_ID)


def store(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id == ADMIN_ID:
        update.message.reply_text("Successfully")
        Db.get_instance().update_commands()
        print(active_chats)
        print(active_requests)
        print(active_commands)
        print(current_list_users)
