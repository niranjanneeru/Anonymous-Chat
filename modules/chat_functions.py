from random import sample

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from .functions import status_code, helper
from data import active_chats, active_requests, active_commands, delete_msg
from database.db import Db
from models.request import Request
from utils import (ACCEPT_CALLBACK_DATA,
                   DECLINE_CALLBACK_DATA, INTEREST_LIST, ACCEPT_REPORT_CALLBACK_DATA, DECLINE_REPORT_CALLBACK_DATA,
                   CANCEL_REQUEST_CALLBACK_DATA)


def set_up_random_chat(update: Update, context: CallbackContext) -> None:
    data = status_code(update.callback_query.message.chat_id)
    if data == 1:
        context.bot.send_message(text=f'``` Close the current chat portal to start a new one ```',
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=update.callback_query.message.chat.id, )
        return
    if data == 0:
        data = active_requests.get(update.callback_query.message.chat.id, None)
        delete_msg(update.callback_query.message.chat_id, context)
        print(data)
        if data[1] == 1:
            keyboard = [[InlineKeyboardButton("CANCEL REQUEST", callback_data=CANCEL_REQUEST_CALLBACK_DATA)]]
            msg_id = context.bot.send_message(update.callback_query.message.chat.id,
                                              """``` You are in request phase Waiting for Accepting```""",
                                              parse_mode=ParseMode.MARKDOWN,
                                              reply_markup=InlineKeyboardMarkup(keyboard)).message_id
            active_commands[update.callback_query.message.chat.id] = msg_id
        elif data[1] == -1:
            keyboard = [[InlineKeyboardButton("ACCEPT", callback_data=ACCEPT_CALLBACK_DATA),
                         InlineKeyboardButton("DECLINE", callback_data=DECLINE_CALLBACK_DATA), ], ]
            msg_id = context.bot.send_message(update.callback_query.message.chat.id,
                                              """``` You are in request phase```""",
                                              parse_mode=ParseMode.MARKDOWN,
                                              reply_markup=InlineKeyboardMarkup(keyboard)).message_id
            active_commands[update.callback_query.message.chat.id] = msg_id
        return

    data = Db.get_instance().read_available_users(update.callback_query.message.chat.id)
    if len(data) == 0:
        context.bot.send_message(text=f'``` Oops! No Users Available try after some time ```',
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=update.callback_query.message.chat.id, )
    else:
        user = sample(data, 1)[0]
        request = Request()
        request.make(update.callback_query.message.chat.id, user.tel_id, 0)
        Db.get_instance().write_request(request)
        active_requests[request.tel_id] = (request.tel_to, 1)
        active_requests[request.tel_to] = (request.tel_id, -1)
        delete_msg(request.tel_id, context)
        keyboard = [[InlineKeyboardButton("CANCEL REQUEST", callback_data=CANCEL_REQUEST_CALLBACK_DATA)]]
        active_commands[request.tel_id] = context.bot.send_message(text=f'``` Waiting for Confirmation ```',
                                                                   parse_mode=ParseMode.MARKDOWN,
                                                                   chat_id=request.tel_id,
                                                                   reply_markup=InlineKeyboardMarkup(
                                                                       keyboard)).message_id
        keyboard = [[InlineKeyboardButton("ACCEPT", callback_data=ACCEPT_CALLBACK_DATA),
                     InlineKeyboardButton("DECLINE", callback_data=DECLINE_CALLBACK_DATA), ], ]
        delete_msg(request.tel_to, context)
        active_commands[request.tel_to] = context.bot.send_message(text=f'``` Anonymous Chat Request ```',
                                                                   parse_mode=ParseMode.MARKDOWN,
                                                                   chat_id=request.tel_to,
                                                                   reply_markup=InlineKeyboardMarkup(
                                                                       keyboard)).message_id
        Db.get_instance().update_user_connected(request.tel_id)
        Db.get_instance().update_user_connected(request.tel_to)


def accept_request(update: Update, context: CallbackContext):
    tel_to = update.callback_query.message.chat.id
    tel_id = active_requests.get(tel_to, None)
    if tel_id:
        tel_id = tel_id[0]
        active_chats[tel_id] = active_requests[tel_id][0]
        active_chats[active_chats[tel_id]] = tel_id
        del active_requests[tel_id]
        del active_requests[active_chats[tel_id]]
        delete_msg(tel_id, context)
        delete_msg(tel_to, context)
        active_commands[tel_id] = context.bot.send_message(text=f'``` Request Accepted ```',
                                                           parse_mode=ParseMode.MARKDOWN,
                                                           chat_id=tel_id).message_id
        context.bot.send_message(text=f'``` The Messages Now on (except Commands will be visible to the Anonymous '
                                      f'person) ```', parse_mode=ParseMode.MARKDOWN,
                                 chat_id=tel_id)
        context.bot.send_message(text=f'``` The Messages Now on (except Commands will be visible to the Anonymous '
                                      f'person) ```', parse_mode=ParseMode.MARKDOWN,
                                 chat_id=tel_to)
        res = Db.get_instance().get_common_interests(tel_id, tel_to)
        data = [INTEREST_LIST[x] for x in res[0].intersection(res[1])]
        if len(data) != 0:
            context.bot.send_message(text=f'``` Common Interest {" ".join(data)}```', parse_mode=ParseMode.MARKDOWN,
                                     chat_id=tel_id)
            context.bot.send_message(text=f'``` Common Interest {" ".join(data)} ```', parse_mode=ParseMode.MARKDOWN,
                                     chat_id=tel_to)
        else:
            context.bot.send_message(
                text=f'``` Interests the Anonymous User have:-  {" ".join([INTEREST_LIST[i] for i in res[1]])}```',
                parse_mode=ParseMode.MARKDOWN,
                chat_id=tel_id)
            context.bot.send_message(
                text=f'``` Interests the Anonymous User have:-  {" ".join([INTEREST_LIST[i] for i in res[0]])} ```',
                parse_mode=ParseMode.MARKDOWN,
                chat_id=tel_to)
        req = Request()
        req.make(tel_id, tel_to, 3)
        Db.get_instance().update_request(req)
    else:
        delete_msg(tel_to, context)
        active_commands[tel_to] = context.bot.send_message(
            text=f'``` Expired Request ```',
            parse_mode=ParseMode.MARKDOWN,
            chat_id=tel_to).message_id


def cancel_request(message, context: CallbackContext):
    tel_id = message.chat.id
    tel_to = active_requests.get(tel_id, None)
    if tel_to:
        tel_to = tel_to[0]
        del active_requests[tel_to]
        del active_requests[tel_id]
        delete_msg(tel_id, context)
        active_commands[tel_id] = context.bot.send_message(text=f'``` Request Cancelled ```',
                                                           parse_mode=ParseMode.MARKDOWN,
                                                           chat_id=tel_id).message_id
        Db.get_instance().update_user_disconnected(tel_id)
        Db.get_instance().update_user_disconnected(tel_to)
        req = Request()
        req.make(tel_id, tel_to, 5)
        Db.get_instance().update_request(req)
    else:
        delete_msg(tel_id, context)
        active_commands[tel_id] = context.bot.send_message(
            text=f'``` Expired Request ```',
            parse_mode=ParseMode.MARKDOWN,
            chat_id=tel_id).message_id


def decline_request(update: Update, context: CallbackContext):
    tel_to = update.callback_query.message.chat.id
    tel_id = active_requests.get(tel_to, None)
    if tel_id:
        tel_id = tel_id[0]
        del active_requests[tel_to]
        del active_requests[tel_id]
        delete_msg(tel_id, context)
        delete_msg(tel_to, context)
        active_commands[tel_id] = context.bot.send_message(text=f'``` Request Cancelled ```',
                                                           parse_mode=ParseMode.MARKDOWN,
                                                           chat_id=tel_id).message_id
        active_commands[tel_to] = context.bot.send_message(text=f'``` Request Cancelled ```',
                                                           parse_mode=ParseMode.MARKDOWN,
                                                           chat_id=tel_to).message_id

        Db.get_instance().update_user_disconnected(tel_id)
        Db.get_instance().update_user_disconnected(tel_to)
        req = Request()
        req.make(tel_id, tel_to, 2)
        Db.get_instance().update_request(req)
    else:
        delete_msg(tel_to, context)
        active_commands[tel_to] = context.bot.send_message(
            text=f'``` Expired Request ```',
            parse_mode=ParseMode.MARKDOWN,
            chat_id=tel_to).message_id


def cancel_chat(update: Update, context: CallbackContext):
    tel_id = active_chats.get(update.callback_query.message.chat.id, None)
    if tel_id:
        Db.get_instance().update_user_disconnected(tel_id)
        Db.get_instance().update_user_disconnected(active_chats[tel_id])
        req = Request()
        req.make(tel_id, active_chats[tel_id], 1)
        Db.get_instance().update_request(req)
        req.make(active_chats[tel_id], tel_id, 1)
        Db.get_instance().update_request(req)
        delete_msg(tel_id, context)
        delete_msg(active_chats[tel_id], context)
        active_commands[tel_id] = context.bot.send_message(text=f'``` Chat Cancelled ```',
                                                           parse_mode=ParseMode.MARKDOWN,
                                                           chat_id=tel_id).message_id
        active_commands[active_chats[tel_id]] = context.bot.send_message(text=f'``` Chat Cancelled ```',
                                                                         parse_mode=ParseMode.MARKDOWN,
                                                                         chat_id=active_chats[tel_id]).message_id
        context.bot.send_message(text="/chat for chat settings",
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=active_chats[tel_id])
        context.bot.send_message(text="/chat for chat settings",
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=tel_id)
        del active_chats[active_chats[tel_id]]
        del active_chats[tel_id]


def report_chat(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("REPORT", callback_data=ACCEPT_REPORT_CALLBACK_DATA),
                 InlineKeyboardButton("CANCEL", callback_data=DECLINE_REPORT_CALLBACK_DATA), ], ]
    delete_msg(update.callback_query.message.chat.id, context)
    active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
        text="""``` Are you sure to block the user? This may blacklist the user and will those this chat portal```""",
        chat_id=update.callback_query.message.chat.id,
        parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard)).message_id


def report_confirmation(update: Update, context: CallbackContext):
    if update.callback_query.data == ACCEPT_REPORT_CALLBACK_DATA:
        Db.get_instance().update_block(active_chats[update.callback_query.message.chat.id])
        cancel_chat(update, context)
    elif update.callback_query.data == DECLINE_CALLBACK_DATA:
        delete_msg(update.callback_query.message.chat.id, context)
        active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
            text="""``` Report Request Closed```""",
            chat_id=update.callback_query.message.chat.id,
            parse_mode=ParseMode.MARKDOWN).message_id
