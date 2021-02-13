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
    with open('active_requests', 'w') as file:
        for i in active_requests:
            file.write(f"{i} {active_requests[i][0]} {active_requests[i][1]}\n")
    with open('active_chats', 'w') as file:
        for i in active_chats:
            file.write(f"{i} {active_chats[i]}\n")
    with open('active_polls', 'w') as file:
        for i in active_polls:
            file.write(f"{i} {asked_questionnaire[i][0]} {asked_questionnaire[i][1]}\n")


def deserialize():
    global current_list_users
    global active_chats
    global active_requests
    global active_commands
    global active_polls
    global asked_questionnaire
    with open('active_requests') as file:
        for i in file:
            if len(data) != 3:
                continue
            data = i.split(' ')
            active_requests[int(data[0].strip())] = (int(data[1].strip()), int(data[2].strip()))
    with open('active_chats') as file:
        for i in file:
            data = i.split(' ')
            if len(data) != 2:
                continue
            active_chats[int(data[0].strip())] = int(data[1].strip())
    with open('active_polls') as file:
        for i in file:
            data = i.split(' ')
            if len(data) != 3:
                continue
            active_polls[int(data[0].strip())] = (int(data[1].strip()), data[2].strip())
