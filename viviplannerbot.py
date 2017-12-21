import time
import telepot
import telegram
from telepot.loop import MessageLoop
from constants import *
from database import Planner

chats = dict()
planner = Planner()


def init_chat_info(chat_id):
    chats[chat_id] = {"state": None,
                      "user_id": None,
                      "event": dict()}


def ask_user(chat_id, state):
    bot.sendMessage(chat_id, '{} is the event?\n\nReply with: /{}.'.format(state.title(), state))


def handle(msg):
    global chats, planner

    chat_id = msg['chat']['id']
    text = msg['text']
    split = text.split(' ', 1)
    command = split[0]
    user = msg['from']['id']

    print('Got command: %s' % command)
    print(msg)

    if chat_id not in chats:
        init_chat_info(chat_id)

    if command == '/new':
        chats[chat_id]["state"] = NEW_EVENT_DESC
        chats[chat_id]["user_id"] = user
        ask_user(chat_id, "what")
    elif chats[chat_id]["state"] == NEW_EVENT_DESC and chats[chat_id]["user_id"] == user and command == '/what':
        chats[chat_id]["state"] = NEW_EVENT_LOC
        chats[chat_id]["event"]["desc"] = split[1]
        ask_user(chat_id, "where")
    elif chats[chat_id]["state"] == NEW_EVENT_LOC and chats[chat_id]["user_id"] == user and command == '/where':
        chats[chat_id]["state"] = NEW_EVENT_TIME
        chats[chat_id]["event"]["loc"] = split[1]
        ask_user(chat_id, "when")
    elif chats[chat_id]["state"] == NEW_EVENT_TIME and chats[chat_id]["user_id"] == user and command == '/when':
        chats[chat_id]["event"]["time"] = split[1]
        plan = chats[chat_id]["event"]
        # bot.sendMessage(chat_id, 'desc: {}\nplace: {}\ntime: {}'.format(plan["desc"], plan["loc"], plan["time"]))
        planner.new_plan(chat_id, plan["desc"], plan["loc"], plan["time"])
        init_chat_info(chat_id)
    elif command == '/cancel':
        if chats[chat_id]["state"] is not None:
            bot.sendMessage(chat_id, 'New event creation cancelled.')
            init_chat_info(chat_id)
        else:
            bot.sendMessage(chat_id, 'No new event currently being created.')
    elif command == '/view':
        bot.sendMessage(chat_id, planner.view_plan(chat_id), parse_mode=telegram.ParseMode.MARKDOWN)


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(1)
