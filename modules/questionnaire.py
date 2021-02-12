from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from data import (active_chats, active_commands, delete_msg, asked_questionnaire,
                  active_polls)
from database.db import Db
from utils import (MENU, OPTION_LIST,
                   QUESTIONNAIRE_SET)


def cancel(update: Update, context: CallbackContext):
    if asked_questionnaire.get(update.message.chat.id, None):
        asked_questionnaire[update.message.chat.id] = False
        delete_msg(update.message.chat.id, context)
        active_commands[update.message.chat.id] = context.bot.send_message(
            text="""``` Questionnaire Operation Cancelled```""", chat_id=update.message.chat.id,
            parse_mode=ParseMode.MARKDOWN).message_id


def parse_questions(update: Update, context: CallbackContext):
    delete_msg(update.message.chat.id, context)
    ques = update.message.text.split('|')
    if Db.get_instance().get_questions(update.message.chat_id):
        Db.get_instance().delete_questions(update.message.chat_id)

    Db.get_instance().add_questions(update.message.chat_id, ques)
    msg = "Entered Questions\n"
    for i in ques:
        msg += f"{ques.index(i) + 1} {i.strip()}\n"
    keyboard = [[InlineKeyboardButton("Edit Questionnaire", callback_data=QUESTIONNAIRE_SET),
                 InlineKeyboardButton("<< Menu", callback_data=MENU), ], ]
    active_commands[update.message.chat.id] = context.bot.send_message(text=f"```{msg}```",
                                                                       parse_mode=ParseMode.MARKDOWN,
                                                                       chat_id=update.message.chat_id,
                                                                       reply_markup=InlineKeyboardMarkup(
                                                                           keyboard)).message_id
    asked_questionnaire[update.message.chat.id] = False


def questionnaire(update: Update, context: CallbackContext):
    chat_id = update.callback_query.message.chat.id
    delete_msg(chat_id, context)
    print(Db.get_instance().get_questions(chat_id))
    if Db.get_instance().get_questions(chat_id) is None:
        active_commands[chat_id] = context.bot.send_message(text="""``` Fill Up the Questionnaire
         1. Separate Questions with a '|'
         2. Yes or No Questions Only
         3. eg:- Have you tripped to Manali? | Is Christopher Nolan Your Favorite? 
         4. Max 500 Characters
         5. /cancel to cancel this operation```""", chat_id=chat_id, parse_mode=ParseMode.MARKDOWN).message_id
        asked_questionnaire[update.callback_query.message.chat.id] = True
    else:
        view_questionnaire(update, context)


def edit_questionnaire(update: Update, context: CallbackContext):
    chat_id = update.callback_query.message.chat_id
    delete_msg(chat_id, context)
    active_commands[chat_id] = context.bot.send_message(text="""``` Fill Up the Questionnaire
             1. Separate Questions with a '|'
             2. Yes or No Questions Only
             3. eg:- Have you tripped to Manali? | Is Christopher Nolan Your Favorite? 
             4. Max 500 Characters
             5. /cancel to cancel this operation```""", chat_id=chat_id, parse_mode=ParseMode.MARKDOWN).message_id
    asked_questionnaire[update.callback_query.message.chat.id] = True


def view_questionnaire(update: Update, context: CallbackContext):
    chat_id = update.callback_query.message.chat_id
    delete_msg(chat_id, context)
    data = Db.get_instance().get_questions(chat_id)
    msg = "Entered Questions\n"
    for i in data:
        msg += f"{data.index(i) + 1} {i.strip()}\n"
    keyboard = [[InlineKeyboardButton("Edit Questionnaire", callback_data=QUESTIONNAIRE_SET),
                 InlineKeyboardButton("<< Menu", callback_data=MENU), ], ]
    active_commands[chat_id] = context.bot.send_message(text=f"```{msg}```",
                                                        parse_mode=ParseMode.MARKDOWN,
                                                        chat_id=chat_id,
                                                        reply_markup=InlineKeyboardMarkup(keyboard)).message_id
    asked_questionnaire[chat_id] = False


def send_questionnaire(update: Update, context: CallbackContext):
    delete_msg(update.callback_query.message.chat.id, context)
    ques = Db.get_instance().get_questions(update.callback_query.message.chat.id)
    for i in ques:
        msg = context.bot.send_poll(active_chats[update.callback_query.message.chat.id],
                                    f"{ques.index(i) + 1}) {i.strip()}",
                                    OPTION_LIST, is_anonymous=False)
        active_polls[msg.poll.id] = (msg.message_id, i)
    active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
        update.callback_query.message.chat.id, "``` Poll Sent Waiting for reply```",
        parse_mode=ParseMode.MARKDOWN).message_id


def handle_answers(update: Update, context: CallbackContext):
    user_id = update.poll_answer.user.id
    poll_id = update.poll_answer.poll_id
    option = OPTION_LIST[update.poll_answer.option_ids[0]]
    ques = active_polls.get(poll_id, None)
    if ques:
        context.bot.send_message(active_chats[user_id], f"""``` {ques[1]} \n Anonymous User answered :- {option}```""",
                                 parse_mode=ParseMode.MARKDOWN)
        del active_polls[poll_id]
        context.bot.delete_message(user_id, ques[0])
