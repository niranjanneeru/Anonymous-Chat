from telegram import Update
from telegram.ext import CallbackContext

from data import serialize, active_chats, active_commands, active_requests
from utils import (ADMIN_ID)


def store(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id == ADMIN_ID:
        update.message.reply_text("Successfully")
        serialize()
        print(active_requests)
        print(active_chats)
        print(active_commands)


def chat_id(update: Update, context: CallbackContext):
    update.message.reply_text(f"Id:- {update.message.chat_id}")
