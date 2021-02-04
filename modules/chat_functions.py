from random import sample

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from data import active_chats, active_requests, active_commands, delete_msg
from database.db import Db
from models.request import Request
from utils import (ACCEPT_CALLBACK_DATA,
                   DECLINE_CALLBACK_DATA, INTEREST_LIST)


def set_up_random_chat(update: Update, context: CallbackContext) -> None:
    data = Db.get_instance().read_available_users(update.callback_query.message.chat.id)
    if len(data) == 0:
        delete_msg(update.callback_query.message.chat.id, context)
        active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
            text=f'``` No Available Users Found ```', parse_mode=ParseMode.MARKDOWN,
            chat_id=update.callback_query.message.chat.id, ).message_id
    else:
        user = sample(data, 1)[0]
        request = Request()
        request.make(update.callback_query.message.chat.id, user.tel_id, 0)
        Db.get_instance().write_request(request)
        active_requests[request.tel_id] = request.tel_to
        active_requests[request.tel_to] = request.tel_id
        delete_msg(request.tel_id, context)
        active_commands[request.tel_id] = context.bot.send_message(text=f'``` Waiting for Confirmation ```',
                                                                   parse_mode=ParseMode.MARKDOWN,
                                                                   chat_id=request.tel_id, ).message_id
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
    tel_id = active_requests[tel_to]
    active_chats[tel_id] = active_requests[tel_id]
    active_chats[active_chats[tel_id]] = tel_id
    del active_requests[tel_id]
    del active_requests[active_chats[tel_id]]
    delete_msg(tel_id, context)
    delete_msg(tel_to, context)
    active_commands[tel_id] = context.bot.send_message(text=f'``` Request Accepted ```', parse_mode=ParseMode.MARKDOWN,
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


def decline_request(update: Update, context: CallbackContext):
    tel_to = update.callback_query.message.chat.id
    tel_id = active_requests[tel_to]
    del active_requests[tel_to]
    del active_requests[tel_id]
    delete_msg(tel_id, context)
    delete_msg(tel_to, context)
    active_commands[tel_id] = context.bot.send_message(text=f'``` Request Cancelled ```', parse_mode=ParseMode.MARKDOWN,
                                                       chat_id=tel_id).message_id
    active_commands[tel_to] = context.bot.send_message(text=f'``` Request Cancelled ```', parse_mode=ParseMode.MARKDOWN,
                                                       chat_id=tel_to).message_id

    Db.get_instance().update_user_disconnected(tel_id)
    Db.get_instance().update_user_disconnected(tel_to)
    req = Request()
    req.make(tel_id, tel_to, 2)
    Db.get_instance().update_request(req)


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
        del active_chats[active_chats[tel_id]]
        del active_chats[tel_id]
