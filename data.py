import pickle

current_list_users = {}
active_requests = {}
active_chats = {}
active_commands = {}
black_list = []
asked_questionnaire = {}
active_polls = {}


def delete_msg(chat_id, context):
    global active_commands
    if chat_id:
        msg_id = active_commands.get(chat_id, None)
        if msg_id:
            print(msg_id)
            context.bot.delete_message(chat_id, msg_id)
            active_commands[chat_id] = None


def serialize():
    with open('active_commands', 'wb') as file:
        pickle.dump(active_commands, file)
    with open('current_list', 'wb') as file:
        pickle.dump(current_list_users, file)
    with open('active_requests', 'wb') as file:
        pickle.dump(active_requests, file)
    with open('active_chats', 'wb') as file:
        pickle.dump(active_chats, file)


def deserialize():
    global current_list_users
    global active_chats
    global active_requests
    global active_commands
    with open('active_commands', 'rb') as file:
        active_commands = pickle.load(file)
    with open('current_list', 'rb') as file:
        current_list_users = pickle.load(file)
    with open('active_requests', 'rb') as file:
        active_requests = pickle.load(file)
    with open('active_chats', 'rb') as file:
        active_chats = pickle.load(file)
