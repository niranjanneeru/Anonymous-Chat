from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from data import current_list_users, active_chats, active_commands, delete_msg, black_list, active_requests
from database.db import Db
from models.user import User
from utils import (WELCOME_TEXT, REGISTRATION_CALLBACK_DATA, PRIVATE_POLICY_CALLBACK_DATA,
                   ABOUT_US_CALLBACK_DATA, ASK_FOR_NAME, MALE_CALLBACK_DATA, FEMALE_CALLBACK_DATA,
                   NEUTRAL_CALLBACK_DATA, RESET_CALLBACK_DATA, RANDOM_CHAT_CALLBACK_DATA, COMMAND_CALLBACK_DATA,
                   INTEREST_LIST, WALKABOUT_CALLBACK_DATA, COMMANDS, ACCEPT_REVEAL_CALLBACK_DATA,
                   DECLINE_REVEAL_CALLBACK_DATA, QUESTIONNAIRE, QUESTIONNAIRE_SENT, CANCEL_REQUEST_CALLBACK_DATA,
                   CLOSE_CHAT, REPORT_CHAT, REVEAL_IDENTITY_REQUEST, ACCEPT_CALLBACK_DATA, DECLINE_CALLBACK_DATA,
                   SKIP_REG_CALLBACK_DATA, ASK_FOR_GENDER, ASK_FOR_ID, ASK_FOR_BATCH, ASK_FOR_INTEREST, PLACEHOLDER,
                   )


def status_code(chat_id: int):
    if active_chats.get(chat_id, None):
        return 1
    elif active_requests.get(chat_id, None):
        return 0
    elif Db.get_instance().read_user_id(chat_id):
        return -1


def status(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    code = status_code(chat_id)
    if code == 1:
        delete_msg(chat_id, context)
        active_commands[chat_id] = context.bot.send_message(chat_id,
                                                            """``` You are in a chat with an anonymous person```""",
                                                            parse_mode=ParseMode.MARKDOWN).message_id
    elif code == 0:
        delete_msg(chat_id, context)
        data = active_requests.get(chat_id, None)
        print(data)
        if data[1] == 1:
            keyboard = [[InlineKeyboardButton("CANCEL REQUEST", callback_data=CANCEL_REQUEST_CALLBACK_DATA)]]
            msg_id = context.bot.send_message(chat_id,
                                              """``` You are in request phase Waiting for Accepting```""",
                                              parse_mode=ParseMode.MARKDOWN,
                                              reply_markup=InlineKeyboardMarkup(keyboard)).message_id
            active_commands[chat_id] = msg_id
        elif data[1] == -1:
            keyboard = [[InlineKeyboardButton("ACCEPT", callback_data=ACCEPT_CALLBACK_DATA),
                         InlineKeyboardButton("DECLINE", callback_data=DECLINE_CALLBACK_DATA), ], ]
            msg_id = context.bot.send_message(chat_id,
                                              """``` You are in request phase```""",
                                              parse_mode=ParseMode.MARKDOWN,
                                              reply_markup=InlineKeyboardMarkup(keyboard)).message_id
            active_commands[chat_id] = msg_id

    elif code == -1:
        delete_msg(chat_id, context)
        active_commands[chat_id] = context.bot.send_message(chat_id,
                                                            """``` You are all set to go Anonymous```""",
                                                            parse_mode=ParseMode.MARKDOWN).message_id


def welcome(chat_id: int, context: CallbackContext) -> None:
    menu = [[InlineKeyboardButton("Let's Start By Knowing Each Other", callback_data=REGISTRATION_CALLBACK_DATA), ],
            [InlineKeyboardButton("Skip Knowing Each Other", callback_data=SKIP_REG_CALLBACK_DATA)],
            [InlineKeyboardButton("Privacy Policy", callback_data=PRIVATE_POLICY_CALLBACK_DATA),
             InlineKeyboardButton("About Us", callback_data=ABOUT_US_CALLBACK_DATA)]]
    delete_msg(chat_id, context)
    active_commands[chat_id] = context.bot.send_message(text=WELCOME_TEXT,
                                                        parse_mode=ParseMode.MARKDOWN,
                                                        chat_id=chat_id,
                                                        reply_markup=InlineKeyboardMarkup(menu)).message_id


def helper(chat_id, context):
    if chat_id in black_list:
        return
    if active_chats.get(chat_id, None):
        if Db.get_instance().get_questions(chat_id):
            menu = [[InlineKeyboardButton("Reveal Identity Request", callback_data=REVEAL_IDENTITY_REQUEST), ],
                    [InlineKeyboardButton("Send Questionnaire", callback_data=QUESTIONNAIRE_SENT), ],
                    [InlineKeyboardButton("Report Chat", callback_data=REPORT_CHAT),
                     InlineKeyboardButton("View/ Edit Questionnaire", callback_data=QUESTIONNAIRE)],
                    [InlineKeyboardButton("Close Chat Portal", callback_data=CLOSE_CHAT), ]]
        else:
            menu = [[InlineKeyboardButton("Reveal Identity Request", callback_data=REVEAL_IDENTITY_REQUEST), ],
                    [InlineKeyboardButton("Report Chat", callback_data=REPORT_CHAT),
                     InlineKeyboardButton("View/ Edit Questionnaire", callback_data=QUESTIONNAIRE)],
                    [InlineKeyboardButton("Close Chat Portal", callback_data=CLOSE_CHAT), ]]
        delete_msg(chat_id, context)
        active_commands[chat_id] = context.bot.send_message(text=WELCOME_TEXT,
                                                            parse_mode=ParseMode.MARKDOWN,
                                                            chat_id=chat_id,
                                                            reply_markup=InlineKeyboardMarkup(
                                                                menu)).message_id
    elif Db.get_instance().read_user_id(chat_id):
        menu = [[InlineKeyboardButton("Random Chat", callback_data=RANDOM_CHAT_CALLBACK_DATA), ],
                [InlineKeyboardButton("Questionnaire", callback_data=QUESTIONNAIRE), ],
                [InlineKeyboardButton("Alter Interest", callback_data=RESET_CALLBACK_DATA), ],
                [InlineKeyboardButton("How This Works", callback_data=WALKABOUT_CALLBACK_DATA),
                 InlineKeyboardButton("Commands", callback_data=COMMAND_CALLBACK_DATA)]]

        delete_msg(chat_id, context)
        active_commands[chat_id] = context.bot.send_message(text=WELCOME_TEXT,
                                                            parse_mode=ParseMode.MARKDOWN,
                                                            chat_id=chat_id,
                                                            reply_markup=InlineKeyboardMarkup(
                                                                menu)).message_id
    else:
        welcome(chat_id, context)


def help_menu(update: Update, context: CallbackContext) -> None:
    helper(update.message.chat.id, context)


def register_user(update: Update, context: CallbackContext):
    chat_id = update.callback_query.message.chat.id
    if Db.get_instance().read_user_id(chat_id) is None:
        if current_list_users.get(chat_id, None) is None:
            delete_msg(chat_id, context)
            active_commands[chat_id] = context.bot.send_message(text=ASK_FOR_NAME,
                                                                parse_mode=ParseMode.MARKDOWN,
                                                                chat_id=chat_id).message_id
            user = User(update.callback_query.message.chat.id)
            current_list_users[update.callback_query.message.chat.id] = user


def ask_gender(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton("He/Him", callback_data=MALE_CALLBACK_DATA),
                 InlineKeyboardButton("She/Her", callback_data=FEMALE_CALLBACK_DATA), ], [
                    InlineKeyboardButton("Prefer Not To Say", callback_data=NEUTRAL_CALLBACK_DATA), ]]
    delete_msg(update.message.chat.id, context)
    active_commands[update.message.chat.id] = context.bot.send_message(text=ASK_FOR_GENDER,
                                                                       parse_mode=ParseMode.MARKDOWN,
                                                                       chat_id=update.message.chat.id,
                                                                       reply_markup=InlineKeyboardMarkup(
                                                                           keyboard)).message_id
    user = current_list_users[update.message.chat.id]
    user.askedGender = True


def check_for_name(update: Update, context: CallbackContext) -> bool:
    user = current_list_users.get(update.message.chat.id, None)
    if user and user.askedName:
        name = update.message.text
        user.set_name(name)
        user.askedName = False
        ask_gender(update, context)
        return True
    return False


def set_gender(update: Update, context: CallbackContext, gender: str) -> None:
    chat_id = update.callback_query.message.chat.id
    user: User = current_list_users.get(chat_id, None)
    if user and user.askedGender:
        if gender == MALE_CALLBACK_DATA:
            user.gender = 1
        elif gender == FEMALE_CALLBACK_DATA:
            user.gender = -1
        user.askedGender = False
        delete_msg(chat_id, context)
        active_commands[chat_id] = context.bot.send_message(text=ASK_FOR_ID,
                                                            parse_mode=ParseMode.MARKDOWN,
                                                            chat_id=chat_id, ).message_id


def check_id(update: Update, context: CallbackContext) -> bool:
    user: User = current_list_users.get(update.message.chat.id, None)
    if user and user.askedId:
        user.set_id(update.message.text)
        user.askedId = False
        delete_msg(update.message.chat.id, context)
        active_commands[update.message.chat.id] = context.bot.send_message(text=ASK_FOR_BATCH,
                                                                           parse_mode=ParseMode.MARKDOWN,
                                                                           chat_id=update.message.chat.id, ).message_id
        return True
    return False


def check_batch(update: Update, context: CallbackContext) -> bool:
    user: User = current_list_users.get(update.message.chat.id, None)
    if user and user.askedBatch:
        user.set_batch(update.message.text)
        user.askedBatch = False
        delete_msg(update.message.chat.id, context)
        context.bot.send_message(text=f'``` Inserted Data\n'
                                      f'Name {user.name}\n'
                                      f'Instagram {user.instagram_id}\n'
                                      f'Gender {user.GENDER[user.gender]}\n'
                                      f'Year {user.batch}```',
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=update.message.chat.id, )
        Db.get_instance().write_user(user)
        Db.get_instance().read_users()
        active_commands[update.message.chat.id] = context.bot.send_poll(update.message.chat.id,
                                                                        ASK_FOR_INTEREST,
                                                                        INTEREST_LIST, allows_multiple_answers=True,
                                                                        is_anonymous=False).message_id
        return True
    return False


def add_poll(update: Update, context: CallbackContext) -> bool:
    user_id = update.poll_answer.user.id
    user: User = current_list_users.get(user_id, None)
    if user and user.askedSkill:
        msg = []
        flag = 0
        for i in update.poll_answer.option_ids:
            Db.get_instance().add_interest(user_id, i)
            msg.append(INTEREST_LIST[i])
            flag += 1
            if flag == 3:
                break
        user.askedSkill = False
        context.bot.send_message(text=f'``` Selected Interest:- {",".join(msg)} ```',
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=user_id, )
        del current_list_users[user_id]
        context.bot.send_message(text=f'``` You are all set to go Anonymous ```',
                                 parse_mode=ParseMode.MARKDOWN,
                                 chat_id=user_id, )
        helper(user_id, context)
        return True
    return False


def send_poll(update: Update, context: CallbackContext) -> None:
    delete_msg(update.callback_query.message.chat.id, context)
    user = Db.get_instance().read_user_id(update.callback_query.message.chat.id)
    user.askedSkill = True
    current_list_users[user.tel_id] = user
    Db.get_instance().delete_interest(user.tel_id)
    active_commands[update.callback_query.message.chat.id] = context.bot.send_poll(
        update.callback_query.message.chat.id,
        ASK_FOR_INTEREST,
        INTEREST_LIST, allows_multiple_answers=True,
        is_anonymous=False).message_id


def about(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(text="``` Welcome to Pigeon```",
                             parse_mode=ParseMode.MARKDOWN,
                             chat_id=update.callback_query.message.chat.id)


def commands(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(text=COMMANDS,
                             parse_mode=ParseMode.MARKDOWN,
                             chat_id=update.callback_query.message.chat.id)


def reveal(update: Update, context: CallbackContext) -> None:
    data = Db.get_instance().read_user_id(update.callback_query.message.chat_id)
    if data:
        if data.name == PLACEHOLDER:
            delete_msg(update.callback_query.message.chat.id, context)
            active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
                text="""``` You haven't provided the details```""", parse_mode=ParseMode.MARKDOWN,
                chat_id=update.callback_query.message.chat.id, ).message_id
            return
        else:
            data = Db.get_instance().read_user_id(active_chats[update.callback_query.message.chat_id])
            if data:
                if data.name == PLACEHOLDER:
                    delete_msg(update.callback_query.message.chat.id, context)
                    active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
                        text="""``` The user who's chatting with you hasn't provided the details```""",
                        parse_mode=ParseMode.MARKDOWN,
                        chat_id=update.callback_query.message.chat.id, ).message_id
                    return
        keyboard = [[InlineKeyboardButton("ACCEPT", callback_data=ACCEPT_REVEAL_CALLBACK_DATA),
                     InlineKeyboardButton("DECLINE", callback_data=DECLINE_REVEAL_CALLBACK_DATA), ], ]
        delete_msg(active_chats.get(update.callback_query.message.chat.id, None), context)
        delete_msg(update.callback_query.message.chat.id, context)
        active_commands[active_chats[update.callback_query.message.chat.id]] = context.bot.send_message(
            text="""``` Reveal Request```""", parse_mode=ParseMode.MARKDOWN,
            chat_id=active_chats[update.callback_query.message.chat.id],
            reply_markup=InlineKeyboardMarkup(
                keyboard)).message_id
        active_commands[update.callback_query.message.chat.id] = context.bot.send_message(
            text="""``` Reveal Request Sent```""", parse_mode=ParseMode.MARKDOWN,
            chat_id=update.callback_query.message.chat.id, ).message_id
    else:
        helper(update.callback_query.message.chat_id, context)


def accept_reveal_request(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat.id
    delete_msg(active_chats.get(user_id, None), context)
    delete_msg(user_id, context)
    data = Db.get_instance().read_user_id(user_id)
    if data:
        msg = f"``` Name:- {data.name}\n Instagram Id:- {data.instagram_id}\n Gender:- {data.GENDER[data.gender]}\n Year:- {data.batch}```"
        context.bot.send_message(text=msg, parse_mode=ParseMode.MARKDOWN,
                                 chat_id=active_chats[user_id])
    data = Db.get_instance().read_user_id(active_chats[user_id])
    if data:
        msg = f"``` Name:- {data.name}\n Instagram Id:- {data.instagram_id}\n Gender:- {data.GENDER[data.gender]}\n Year:- {data.batch}```"
        context.bot.send_message(text=msg, parse_mode=ParseMode.MARKDOWN,
                                 chat_id=user_id)


def decline_reveal_request(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.message.chat.id
    delete_msg(active_chats.get(user_id, None), context)
    delete_msg(user_id, context)
    active_commands[active_chats[user_id]] = context.bot.send_message(text="``` Reveal Request Declined```",
                                                                      parse_mode=ParseMode.MARKDOWN,
                                                                      chat_id=active_chats[user_id]).message_id
    active_commands[user_id] = context.bot.send_message(text="``` Reveal Request Declined```",
                                                        parse_mode=ParseMode.MARKDOWN,
                                                        chat_id=user_id).message_id


def skip_process(message, context: CallbackContext):
    chat_id = message.chat_id
    if not Db.get_instance().read_user_id(chat_id):
        if current_list_users.get(chat_id, None):
            user = current_list_users[chat_id]
            Db.get_instance().write_user(user)
            del current_list_users[chat_id]
        else:
            user = User(chat_id)
            Db.get_instance().write_user(user)
    delete_msg(message.chat.id, context)
    user = User(chat_id)
    user.askedId = False
    user.askedGender = False
    user.askedName = False
    user.askedBatch = False
    current_list_users[chat_id] = user
    active_commands[message.chat.id] = context.bot.send_poll(chat_id,
                                                             ASK_FOR_INTEREST,
                                                             INTEREST_LIST, allows_multiple_answers=True,
                                                             is_anonymous=False).message_id


def skip(update: Update, context: CallbackContext):
    skip_process(update.message, context)
