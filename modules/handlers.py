from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from data import active_chats, black_list, asked_questionnaire
from utils import (REGISTRATION_CALLBACK_DATA, MALE_CALLBACK_DATA, FEMALE_CALLBACK_DATA,
                   NEUTRAL_CALLBACK_DATA, RANDOM_CHAT_CALLBACK_DATA, RESET_CALLBACK_DATA, COMMAND_CALLBACK_DATA,
                   ABOUT_US_CALLBACK_DATA, PRIVATE_POLICY_CALLBACK_DATA, WALKABOUT_CALLBACK_DATA, ACCEPT_CALLBACK_DATA,
                   DECLINE_CALLBACK_DATA, CLOSE_CHAT, REVEAL_IDENTITY_REQUEST, REPORT_CHAT, QUESTIONNAIRE,
                   ACCEPT_REVEAL_CALLBACK_DATA, DECLINE_REVEAL_CALLBACK_DATA, ACCEPT_REPORT_CALLBACK_DATA,
                   DECLINE_REPORT_CALLBACK_DATA, MENU, QUESTIONNAIRE_SET, VIEW_QUES, QUESTIONNAIRE_SENT,
                   CANCEL_REQUEST_CALLBACK_DATA)
from .chat_functions import (set_up_random_chat, accept_request, decline_request, cancel_chat, report_chat,
                             report_confirmation, cancel_request)
from .functions import (register_user, check_for_name, set_gender, check_id, check_batch, add_poll, about, commands,
                        accept_reveal_request, reveal, decline_reveal_request, send_poll, helper)
from .questionnaire import (questionnaire, parse_questions, edit_questionnaire, view_questionnaire, send_questionnaire,
                            handle_answers)


def callback_query_handler(update: Update, context: CallbackContext) -> None:
    if update.callback_query.message.chat.id in black_list:
        return
    if update.callback_query.data == MENU:
        helper(update.callback_query.message.chat_id, context)
    elif update.callback_query.data == REGISTRATION_CALLBACK_DATA:
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
        send_poll(update, context)
    elif update.callback_query.data == QUESTIONNAIRE:
        questionnaire(update, context)
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
    elif update.callback_query.data == REPORT_CHAT:
        report_chat(update, context)
    elif update.callback_query.data == ACCEPT_REPORT_CALLBACK_DATA or update.callback_query.data == DECLINE_REPORT_CALLBACK_DATA:
        report_confirmation(update, context)
    elif update.callback_query.data == QUESTIONNAIRE_SET:
        edit_questionnaire(update, context)
    elif update.callback_query.data == VIEW_QUES:
        view_questionnaire(update, context)
    elif update.callback_query.data == QUESTIONNAIRE_SENT:
        send_questionnaire(update, context)
    elif update.callback_query.data == CANCEL_REQUEST_CALLBACK_DATA:
        cancel_request(update, context)


def message_handler(update: Update, context: CallbackContext) -> None:
    if update.message.chat.id in black_list:
        return
    if check_for_name(update, context):
        return
    elif check_id(update, context):
        return
    elif check_batch(update, context):
        return
    if asked_questionnaire.get(update.message.chat.id, None):
        parse_questions(update, context)
        return
    if active_chats.get(update.message.chat.id, None):
        if update.message.text.find('@'):
            context.bot.send_message(text=update.message.text,
                                     chat_id=active_chats[update.message.chat.id])
        else:
            context.bot.send_message(text=update.message.text, parse_mode=ParseMode.MARKDOWN,
                                     chat_id=active_chats[update.message.chat.id])


def sticker_handler(update: Update, context: CallbackContext):
    if update.message.chat.id in black_list:
        return
    if active_chats.get(update.message.chat.id, None):
        context.bot.send_sticker(sticker=update.message.sticker, chat_id=active_chats[update.message.chat.id])


def poll_handler(update: Update, context: CallbackContext):
    print("Here")
    print(update)


def poll_answer_handler(update: Update, context: CallbackContext):
    if update.poll_answer.user.id in black_list:
        return
    if add_poll(update, context):
        return
    print(update)
    handle_answers(update, context)


def message_all_handler(update: Update, context: CallbackContext):
    if update.message.chat.id in black_list:
        return
    update.message.reply_markdown("""``` Files Sharing Not Supported according to privacy policy```""")
