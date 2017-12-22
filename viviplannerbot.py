import time
import telepot
import telegram
from telepot.loop import MessageLoop
from constants import *
from database import Planner
from datetimemgr import *

chats = dict()
planner = Planner()


def init_chat_info(chat_id):
    chats[chat_id] = {"state": None,
                      "user_id": None,
                      "event": dict()}


def ask_user(chat_id, state):
    bot.sendMessage(chat_id,
                    '_{}_ is the event?\n\nReply using /{}.'.format(state.title(), state),
                    parse_mode=telegram.ParseMode.MARKDOWN)


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
        bot.sendMessage(chat_id, '*Planning a new event...* 🤔', parse_mode=telegram.ParseMode.MARKDOWN)
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
        string = split[1]
        chats[chat_id]["event"]["time"] = str2datetime(string)

        # Save to database
        plan = chats[chat_id]["event"]
        planner.new_plan(chat_id, plan["desc"], plan["loc"], plan["time"])
        bot.sendMessage(chat_id, "*New event added!* 😘", parse_mode=telegram.ParseMode.MARKDOWN)
        init_chat_info(chat_id)         # Reset
    elif command == '/cancel':
        if chats[chat_id]["state"] is not None:
            bot.sendMessage(chat_id, 'The current operation is cancelled. ☺')
            init_chat_info(chat_id)     # Reset
        else:
            bot.sendMessage(chat_id, 'There is no current operation. 😅')
    elif command == '/view':
        bot.sendMessage(chat_id, planner.view_plan(chat_id), parse_mode=telegram.ParseMode.MARKDOWN)
    # TODO: elif command == '/help':


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(1)
