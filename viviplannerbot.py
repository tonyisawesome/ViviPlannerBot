import time
import telepot
import telegram
import util
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
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


def query_user(chat_id, state):
    bot.sendMessage(chat_id,
                    '_{}_ is the event?'.format(state.title(), state),
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=ForceReply())


def send_msg(chat_id, msg=""):
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
        text, events = planner.show_all(chat_id)
        send_msg(chat_id, msg=text)


def show_menu(chat_id, from_info):
    button_list = [
        InlineKeyboardButton(text="New Event", callback_data="/new"),
        InlineKeyboardButton(text="Edit Event", callback_data="/edit"),
        InlineKeyboardButton(text="Delete Event", callback_data="/delete"),
        InlineKeyboardButton(text="Show All Events", callback_data="/showall")
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, n_cols=2))
    user_id, first_name = from_info['id'], from_info['first_name']
    bot.sendMessage(chat_id,
                    "Hi, [{}](tg://user?id={})~ What can I do for nya? 😺".format(first_name, user_id),
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=reply_markup)


def init_new_event_query(chat_id, from_info):
    user_id, first_name = from_info['id'], from_info['first_name']
    send_msg(chat_id,
             msg='[{}](tg://user?id={}) *is planning a new event...* 🤔'.format(first_name, user_id))
    query_user(chat_id, "what")


def show_events(chat_id):
    text, events = planner.show_all(chat_id)
    button_list = [InlineKeyboardButton(text=desc, callback_data="/show {}".format(i)) for i, desc in enumerate(events)]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list))
    bot.sendMessage(chat_id,
                    text,
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=reply_markup)


def show_event(chat_id, i):
    button_list = [InlineKeyboardButton(text="Edit Event", callback_data="/edit"),
                   InlineKeyboardButton(text="Delete Event", callback_data="/delete")]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, n_cols=2))
    bot.sendMessage(chat_id,
                    planner.show(chat_id, i),
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=reply_markup)


def on_chat_message(msg):
    global chats, planner

    chat_id = msg['chat']['id']
    text = msg['text']
    user = msg['from']['id']
    command, content = util.parse(text)

    print('Got command: %s' % command)
    print('Got content: %s' % content)
    print(msg)

    if chat_id not in chats:
        init_chat_info(chat_id)

    if command == '/new':
        init_new_event_query(chat_id, msg['from'])
    elif 'reply_to_message' in msg and msg['reply_to_message']['from']['is_bot']:
        reply_to_text = msg['reply_to_message']['text']

        if reply_to_text == 'What is the event?':
            chats[chat_id]["event"]["desc"] = content
            query_user(chat_id, "where")
        elif reply_to_text == 'Where is the event?':
            chats[chat_id]["event"]["loc"] = content
            query_user(chat_id, "when")
        elif reply_to_text == 'When is the event?':
            chats[chat_id]["event"]["time"] = str2datetime(content)

            # Save to database
            plan = chats[chat_id]["event"]
            planner.new_plan(chat_id, plan["desc"], plan["loc"], plan["time"])
            send_msg(chat_id, msg=planner.show(chat_id, -1))
            send_msg(chat_id, msg="*New event added!* 😘")
        else:
            send_msg(chat_id, msg="_Nya? わかりません…_ 😿")
    elif command == '/show':
        try:
            i = int(content) - 1

            if -1 < i < len(planner.plans[chat_id]):
                show_event(chat_id, i)
            else:
                show_exception(chat_id, NO_EVENT_FOUND)
        except ValueError:
            print("ValueError")
            show_exception(chat_id, VALUE_ERROR)
        except KeyError:
            print("KeyError")
            show_exception(chat_id, NO_EVENT_FOUND)
    elif command == '/showall':
        show_events(chat_id)
    elif command == '/edit':
        try:
            desc = planner.get_desc(chat_id, int(content) - 1)

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
            send_msg(chat_id, msg=planner.delete(chat_id, int(content) - 1))
            send_msg(chat_id, msg=planner.show_all(chat_id))
        except ValueError:
            show_exception(chat_id, VALUE_ERROR)
        except IndexError:
            show_exception(chat_id, VALUE_ERROR)
    elif chats[chat_id]["user_id"] == user and command == '/abort':
        if chats[chat_id]["state"] is not None:
            send_msg(chat_id, msg='The current operation is cancelled. ☺')
            init_chat_info(chat_id)     # Reset
        else:
            send_msg(chat_id, msg='There is currently no operation. 😅')
    # TODO: elif command == '/help':
    elif command == '/menu':
        show_menu(chat_id, msg['from'])
    else:
        send_msg(chat_id, msg="_My wish is your command._ 😏")


def on_callback_query(msg):
    global chats

    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['message']['chat']['id']
    print(msg)

    if chat_id not in chats:
        init_chat_info(chat_id)

    if query_data == '/new':
        init_new_event_query(chat_id, msg['from'])
        bot.answerCallbackQuery(query_id, "EXCITING! Please tell me... 😻")
    elif query_data == '/showall':
        show_events(chat_id)
        bot.answerCallbackQuery(query_id)
    elif '/show' in query_data:
        show_event(chat_id, int(query_data.split(' ', 1)[1]))
        bot.answerCallbackQuery(query_id)
    elif query_data == '/delete':
        bot.answerCallbackQuery(query_id, "Are you sure?? 🙀")


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(1)
