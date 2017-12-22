import time
import telepot
import telegram
import util
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
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


def show_exception(chat_id, exception):
    if exception == VALUE_ERROR:
        send_msg(chat_id, "Please input a *number*...")
        time.sleep(0.5)
        send_msg(chat_id, "... or _master_ will punish me. 😭")
    elif exception == NO_EVENT_FOUND:
        send_msg(chat_id, msg="*The event is not found!* 😞")
        send_msg(chat_id, msg=planner.show_all(chat_id))


def on_chat_message(msg):
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
    elif command == '/show':
        try:
            msg = planner.show(chat_id, int(split[1]) - 1)

            if msg is not None:
                send_msg(chat_id, msg=msg)
            else:
                show_exception(chat_id, NO_EVENT_FOUND)
        except ValueError:
            print("ValueError")
            show_exception(chat_id, VALUE_ERROR)
        except IndexError:
            print("IndexError")
            show_exception(chat_id, VALUE_ERROR)
    elif command == '/showall':
        send_msg(chat_id, msg=planner.show_all(chat_id))
    elif command == '/edit':
        try:
            desc = planner.get_desc(chat_id, int(split[1]) - 1)

            if desc is None:
                show_exception(chat_id, NO_EVENT_FOUND)
            else:
                send_msg(chat_id, msg="Editing event: _{}_...".format(desc))
        except ValueError:
            show_exception(chat_id, VALUE_ERROR)
        except IndexError:
            show_exception(chat_id, VALUE_ERROR)
    # TODO: elif command == '/setdescription':
    # TODO: elif command == '/setlocation':
    # TODO: elif command == '/settime':
    elif command == '/delete':
        try:
            send_msg(chat_id, msg=planner.delete(chat_id, int(split[1]) - 1))
            send_msg(chat_id, msg=planner.show_all(chat_id))
        except ValueError:
            show_exception(chat_id, VALUE_ERROR)
        except IndexError:
            show_exception(chat_id, VALUE_ERROR)
    elif command == '/abort':
        if chats[chat_id]["state"] is not None:
            send_msg(chat_id, msg='The current operation is cancelled. ☺')
            init_chat_info(chat_id)     # Reset
        else:
            send_msg(chat_id, msg='There is currently no operation. 😅')
    # TODO: elif command == '/help':
    elif command == '/test':
        button_list = [
            InlineKeyboardButton(text="col1", callback_data="1"),
            InlineKeyboardButton(text="col2", callback_data="2"),
            InlineKeyboardButton(text="row 2", callback_data="3")
        ]

        reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, n_cols=2))
        bot.sendMessage(chat_id, "A two-column menu", reply_markup=reply_markup)
    else:
        send_msg(chat_id, msg="_My wish is your command._ 😏")


def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['message']['chat']['id']
    # print(msg)

    bot.answerCallbackQuery(query_id, text='Got it!')


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(1)
