from telegram import Update, ParseMode, PollOption
from telegram.ext import CallbackContext
from utils import (REGISTRATION_CALLBACK_DATA, MALE_CALLBACK_DATA, FEMALE_CALLBACK_DATA,
                   NEUTRAL_CALLBACK_DATA, RANDOM_CHAT_CALLBACK_DATA, RESET_CALLBACK_DATA, COMMAND_CALLBACK_DATA,
                   ABOUT_US_CALLBACK_DATA, PRIVATE_POLICY_CALLBACK_DATA, WALKABOUT_CALLBACK_DATA, ACCEPT_CALLBACK_DATA,
                   DECLINE_CALLBACK_DATA, CLOSE_CHAT, INTEREST_LIST, REVEAL_IDENTITY_REQUEST,
                   ACCEPT_REVEAL_CALLBACK_DATA, DECLINE_REVEAL_CALLBACK_DATA)
from .functions import register_user, check_for_name, set_gender, check_id, check_batch, add_poll, about, commands, \
    accept_reveal_request, reveal, decline_reveal_request
from .chat_functions import set_up_random_chat, accept_request, decline_request, cancel_chat
from data import active_chats
from database.db import Db

message_id = ''


def callback_query_handler(update: Update, context: CallbackContext) -> None:
    if update.callback_query.data == REGISTRATION_CALLBACK_DATA:
        register_user(update, context)
    elif update.callback_query.data == MALE_CALLBACK_DATA or update.callback_query.data == FEMALE_CALLBACK_DATA or update.callback_query.data == NEUTRAL_CALLBACK_DATA:
        set_gender(update, context, update.callback_query.data)
    elif update.callback_query.data == RANDOM_CHAT_CALLBACK_DATA:
        set_up_random_chat(update, context)
    elif update.callback_query.data == ACCEPT_CALLBACK_DATA:
        accept_request(update, context)
    elif update.callback_query.data == DECLINE_CALLBACK_DATA:
        decline_request(update, context)
    elif update.callback_query.data == CLOSE_CHAT:
        cancel_chat(update, context)
    elif update.callback_query.data == ABOUT_US_CALLBACK_DATA:
        about(update, context)
    elif update.callback_query.data == RESET_CALLBACK_DATA:
        pass  # todo questionnaire
    elif update.callback_query.data == PRIVATE_POLICY_CALLBACK_DATA:
        context.bot.send_message(text="https://telegra.ph/Privacy-Policy-for-Under-25-TKMCE-02-03",
                                 chat_id=update.callback_query.message.chat.id)
    elif update.callback_query.data == COMMAND_CALLBACK_DATA:
        commands(update, context)
    elif update.callback_query.data == WALKABOUT_CALLBACK_DATA:
        pass  # todo how it works
    elif update.callback_query.data == REVEAL_IDENTITY_REQUEST:
        reveal(update, context)
    elif update.callback_query.data == ACCEPT_REVEAL_CALLBACK_DATA:
        accept_reveal_request(update, context)
    elif update.callback_query.data == DECLINE_REVEAL_CALLBACK_DATA:
        decline_reveal_request(update, context)


def message_handler(update: Update, context: CallbackContext) -> None:
    if check_for_name(update, context):
        return
    elif check_id(update, context):
        return
    elif check_batch(update, context):
        return
    if active_chats.get(update.message.chat.id, None):
        context.bot.send_message(text=update.message.text, parse_mode=ParseMode.MARKDOWN,
                                 chat_id=active_chats[update.message.chat.id])


def poll_handler(update: Update, context: CallbackContext):
    print("Here")
    print(update)


def poll_answer_handler(update: Update, context: CallbackContext):
    add_poll(update, context)
