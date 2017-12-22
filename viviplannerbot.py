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


def send_msg(chat_id, msg="", state=""):
    if state:
        msg = '_{}_ is the event?\n\nReply using /{}'.format(state.title(), state)

    bot.sendMessage(chat_id,
                    msg,
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
        send_msg(chat_id, msg='*Planning a new event...* 🤔')
        send_msg(chat_id, state="what")
    elif chats[chat_id]["state"] == NEW_EVENT_DESC and chats[chat_id]["user_id"] == user and command == '/what':
        chats[chat_id]["state"] = NEW_EVENT_LOC
        chats[chat_id]["event"]["desc"] = split[1]
        send_msg(chat_id, state="where")
    elif chats[chat_id]["state"] == NEW_EVENT_LOC and chats[chat_id]["user_id"] == user and command == '/where':
        chats[chat_id]["state"] = NEW_EVENT_TIME
        chats[chat_id]["event"]["loc"] = split[1]
        send_msg(chat_id, state="when")
    elif chats[chat_id]["state"] == NEW_EVENT_TIME and chats[chat_id]["user_id"] == user and command == '/when':
        string = split[1]
        chats[chat_id]["event"]["time"] = str2datetime(string)

        # Save to database
        plan = chats[chat_id]["event"]
        planner.new_plan(chat_id, plan["desc"], plan["loc"], plan["time"])
        send_msg(chat_id, msg=planner.show(chat_id, -1))
        send_msg(chat_id, msg="*New event added!* 😘")
        init_chat_info(chat_id)         # Reset
    elif command == '/cancel':
        if chats[chat_id]["state"] is not None:
            send_msg(chat_id, msg='The current operation is cancelled. ☺')
            init_chat_info(chat_id)     # Reset
        else:
            send_msg(chat_id, msg='There is no current operation. 😅')
    elif command == '/showall':
        send_msg(chat_id, msg=planner.show_all(chat_id))
    elif command == '/show':
        if len(split) < 2:
            send_msg(chat_id, msg="Please enter a number from /showall to show the event's detail.")
        else:
            try:
                send_msg(chat_id, planner.show(chat_id, int(split[1]) - 1))
            except ValueError:
                send_msg(chat_id, "Please enter a *number*, or my master will punish me... 😭")
    # TODO: elif command == '/edit':
    # TODO: elif command == '/description':
    # TODO: elif command == '/location':
    # TODO: elif command == '/time':
    elif command == '/delete':
        if len(split) < 2:
            send_msg(chat_id, msg="Please enter a number from /showall to remove an event.")
        else:
            try:
                send_msg(chat_id, msg=planner.delete(chat_id, int(split[1]) - 1))
            except ValueError:
                send_msg(chat_id, "Please enter a *number*, or my master will punish me... 😭")
    # TODO: elif command == '/help':
    else:
        send_msg(chat_id, msg="_My wish is your command._ 😏")


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(1)
