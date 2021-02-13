import html
import json

from telegram import Update, ParseMode, error
from telegram.ext import CallbackContext
import traceback
import logging
from database.db import Db
from .functions import status_code, helper
from .chat_functions import cancel_request
from data import active_chats, active_requests, active_commands

from utils import ADMIN_ID


def error_handle(update: Update, context: CallbackContext):
    logger = logging.getLogger()
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    print(context.error)
    if isinstance(context.error, error.BadRequest):
        update.message.reply_markdown("``` Kindly Repeat the process ```")
        active_commands[update.message.chat_id] = None
    elif isinstance(context.error, error.Unauthorized):
        if status_code(update.message.chat_id) == 1:
            context.bot.send_message(update.message.chat_id,
                                     "``` The Anonymous user blocked the chat bot so we are stopping the chat````",
                                     parse_mode=ParseMode.MARKDOWN, )
            Db.get_instance().delete_user(active_chats[update.message.chat_id])
            Db.get_instance().update_user_disconnected(update.message.chat_id)
            del active_chats[update.message.chat_id]
        elif status_code(update.message.chat_id) == 0:
            context.bot.send_message(update.message.chat_id,
                                     "``` The Anonymous user blocked the chat bot so make another request````",
                                     parse_mode=ParseMode.MARKDOWN, )
            cancel_request(update.message, context)
            Db.get_instance().delete_user(active_requests[update.message.chat_id])
    elif isinstance(context.error, error.TimedOut):
        context.bot.send_message(update.message.chat_id,
                                 "``` Connection Timed Out Repeat the process````",
                                 parse_mode=ParseMode.MARKDOWN, )
        helper(update.message.chat_id, context)
    tb_string = ''.join(tb_list)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )
    context.bot.send_message(chat_id=ADMIN_ID, text=message, parse_mode=ParseMode.HTML)
