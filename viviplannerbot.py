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
                      "event_selected": None,
                      "event": dict()}


def query_user_new(chat_id, from_info, query):
    user_id, first_name = from_info['id'], from_info['first_name']
    bot.sendMessage(chat_id,
                    '[{}](tg://user?id={}), _{}_ is the event?'.format(first_name,
                                                                       user_id,
                                                                       query),
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=ForceReply(selective=True))


emojis = {'description': '📝', 'location': '🏖', 'date': '📆', 'time': '🕜🕡'}


def query_user_edit(chat_id, from_info, i, query):
    user_id, first_name = from_info['id'], from_info['first_name']

    if query == 'description':
        content = planner.get_desc(chat_id, i)
    elif query == 'location':
        content = planner.get_loc(chat_id, i)
    elif query == 'date':
        content = planner.get_date(chat_id, i)
    elif query == 'time':
        content = planner.get_time(chat_id, i)
    else:
        content = ""

    bot.sendMessage(chat_id,
                    "[{}](tg://user?id={}) *is editing the {} {}:*\n\n{}".format(first_name,
                                                                                 user_id,
                                                                                 query,
                                                                                 emojis[query],
                                                                                 content),
                    parse_mode=telegram.ParseMode.MARKDOWN,
                    reply_markup=ForceReply(selective=True))


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


def show_menu(chat_id, from_info, msg_id=None):
    button_list = [
        InlineKeyboardButton(text="New Event", callback_data="/new"),
        InlineKeyboardButton(text="Edit Event", callback_data="/edit"),
        InlineKeyboardButton(text="Delete Event", callback_data="/delete"),
        InlineKeyboardButton(text="Events List", callback_data="/all")
    ]

    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, n_cols=2))
    user_id, first_name = from_info['id'], from_info['first_name']
    msg = "Hi, [{}](tg://user?id={})~ What can I do for nya? 😺".format(first_name, user_id)

    if msg_id:
        bot.editMessageText((chat_id, msg_id),
                            msg,
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id,
                        msg,
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=reply_markup)

    chats[chat_id]['event_selected'] = None     # Reset


def init_new_event_query(chat_id, from_info):
    user_id, first_name = from_info['id'], from_info['first_name']
    send_msg(chat_id,
             msg='[{}](tg://user?id={}) *is planning a new event...* 🤔'.format(first_name, user_id))
    query_user_new(chat_id, from_info, "what")


def show_events(chat_id, cmd, msg_id=None):
    text, events = planner.show_all(chat_id)
    button_list = [InlineKeyboardButton(text=desc, callback_data="{} {}".format(cmd, i)) for i, desc in enumerate(events)]
    footer_buttons = [InlineKeyboardButton(text="« Back to Main Menu", callback_data="/menu")]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, footer_buttons=footer_buttons))

    if msg_id:
        bot.editMessageText((chat_id, msg_id),
                            text,
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id,
                        text,
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=reply_markup)

    return events


def show_event(chat_id, i, msg_id=None):
    button_list = [InlineKeyboardButton(text="Edit Event", callback_data="/edit"),
                   InlineKeyboardButton(text="Delete Event", callback_data="/delete"),
                   InlineKeyboardButton(text="« Back to Main Menu", callback_data="/menu")]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, n_cols=2))
    msg = planner.show(chat_id, i)

    if msg_id:
        bot.editMessageText((chat_id, msg_id),
                            msg,
                            parse_mode=telegram.ParseMode.MARKDOWN,
                            reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id,
                        msg,
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=reply_markup)

    chats[chat_id]['event_selected'] = i


def edit_event(chat_id, msg_id, i):
    button_list = [InlineKeyboardButton(text="Edit Description", callback_data="/setdescription"),
                   InlineKeyboardButton(text="Edit Location", callback_data="/setlocation"),
                   InlineKeyboardButton(text="Edit Date", callback_data="/setdate"),
                   InlineKeyboardButton(text="Edit Time", callback_data="/settime"),
                   InlineKeyboardButton(text="« Back to Main Menu", callback_data="/menu")]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=util.build_menu(button_list, n_cols=2))
    bot.editMessageText((chat_id, msg_id),
                        planner.show(chat_id, i),
                        parse_mode=telegram.ParseMode.MARKDOWN,
                        reply_markup=reply_markup)
    # bot.sendMessage(chat_id,
    #                 planner.show(chat_id, i),
    #                 parse_mode=telegram.ParseMode.MARKDOWN,
    #                 reply_markup=reply_markup)
    chats[chat_id]['event_selected'] = i


def add_event(chat_id, plan, from_info):
    user_id, first_name = from_info['id'], from_info['first_name']
    planner.new_plan(chat_id, plan["desc"], plan["loc"], plan["dt"])
    send_msg(chat_id, msg="[{}](tg://user?id={}) *added a new event!* 😘".format(first_name, user_id))
    show_event(chat_id, -1)


def edit_desc(chat_id, i, desc):
    send_msg(chat_id, planner.set_desc(chat_id, i, desc))
    show_event(chat_id, i)


def edit_loc(chat_id, i, loc):
    send_msg(chat_id, planner.set_loc(chat_id, i, loc))
    show_event(chat_id, i)


def edit_date(chat_id, i, date):
    send_msg(chat_id, planner.set_date(chat_id, i, date))
    show_event(chat_id, i)


def edit_time(chat_id, i, t):
    send_msg(chat_id, planner.set_time(chat_id, i, t))
    show_event(chat_id, i)


def on_chat_message(msg):
    global chats, planner

    chat_id = msg['chat']['id']
    text = msg['text']
    command, content = util.parse(text)

    print('Got command: %s' % command)
    print('Got content: %s' % content)
    print(msg)

    if chat_id not in chats:
        init_chat_info(chat_id)

    if command == '/menu':
        show_menu(chat_id, msg['from'])
    elif command == '/new':
        init_new_event_query(chat_id, msg['from'])
    elif 'reply_to_message' in msg and msg['reply_to_message']['from']['is_bot']:
        reply_to_text = msg['reply_to_message']['text']

        if 'what is the event?' in reply_to_text.lower():
            chats[chat_id]["event"]["desc"] = content
            query_user_new(chat_id, msg['from'], "where")
        elif 'where is the event?' in reply_to_text.lower():
            chats[chat_id]["event"]["loc"] = content
            query_user_new(chat_id, msg['from'], "when")
        elif 'when is the event?' in reply_to_text.lower():
            # chats[chat_id]["event"]["dt"] = str2datetime(content)
            chats[chat_id]["event"]["dt"] = datetime2str(get_datetime(content))

            # Save to database
            add_event(chat_id, chats[chat_id]["event"], msg['from'])
        elif "editing the description" in reply_to_text:
            edit_desc(chat_id, chats[chat_id]['event_selected'], content)
        elif "editing the location" in reply_to_text:
            edit_loc(chat_id, chats[chat_id]['event_selected'], content)
        elif "editing the date" in reply_to_text:
            edit_date(chat_id, chats[chat_id]['event_selected'], content)
        elif "editing the time" in reply_to_text:
            edit_time(chat_id, chats[chat_id]['event_selected'], content)
        else:
            send_msg(chat_id, msg="Nya? わかりません… 😿")
    elif command == '/all':
        show_events(chat_id, '/show')
    elif command == '/help':
        send_msg(chat_id, "You can start by /menu! Nya~ 😽")
    # elif command == '/show':
    #     try:
    #         i = int(content) - 1
    #
    #         if -1 < i < len(planner.plans[chat_id]):
    #             show_event(chat_id, i)
    #         else:
    #             show_exception(chat_id, NO_EVENT_FOUND)
    #     except ValueError:
    #         print("ValueError")
    #         show_exception(chat_id, VALUE_ERROR)
    #     except KeyError:
    #         print("KeyError")
    #         show_exception(chat_id, NO_EVENT_FOUND)
    # elif command == '/edit':
    #     try:
    #         desc = planner.get_desc(chat_id, int(content) - 1)
    #
    #         if desc is None:
    #             show_exception(chat_id, NO_EVENT_FOUND)
    #         else:
    #             send_msg(chat_id, msg="Editing event: _{}_...".format(desc))
    #     except ValueError:
    #         show_exception(chat_id, VALUE_ERROR)
    #     except IndexError:
    #         show_exception(chat_id, VALUE_ERROR)
    # elif command == '/delete':
    #     try:
    #         send_msg(chat_id, msg=planner.delete(chat_id, int(content) - 1))
    #         send_msg(chat_id, msg=planner.show_all(chat_id))
    #     except ValueError:
    #         show_exception(chat_id, VALUE_ERROR)
    #     except IndexError:
    #         show_exception(chat_id, VALUE_ERROR)
    # elif chats[chat_id]["user_id"] == user and command == '/abort':
    #     if chats[chat_id]["state"] is not None:
    #         send_msg(chat_id, msg='The current operation is cancelled. ☺')
    #         init_chat_info(chat_id)     # Reset
    #     else:
    #         send_msg(chat_id, msg='There is currently no operation. 😅')
    else:
        send_msg(chat_id, msg="_My wish is your command._ 😏")


def on_callback_query(msg):
    global chats

    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    chat_id = msg['message']['chat']['id']
    msg_id = msg['message']['message_id']
    print(msg)

    if chat_id not in chats:
        init_chat_info(chat_id)

    if query_data == '/new':
        bot.answerCallbackQuery(query_id, "EXCITING! Please tell me... 😻")
        init_new_event_query(chat_id, msg['from'])
    elif query_data == '/all':
        text = "Let's go somewhere! GO! GO! GO! 😹" if not show_events(chat_id, '/show', msg_id=msg_id) else ""
        bot.answerCallbackQuery(query_id, text)
    elif '/show' in query_data:
        show_event(chat_id, int(query_data.split(' ', 1)[1]), msg_id=msg_id)
        bot.answerCallbackQuery(query_id)
    elif '/edit' in query_data:
        if chats[chat_id]['event_selected'] is not None:
            edit_event(chat_id, msg_id, chats[chat_id]['event_selected'])
        elif len(query_data.split(' ', 1)) == 2:
            edit_event(chat_id, msg_id, int(query_data.split(' ', 1)[1]))
        else:
            show_events(chat_id, '/edit', msg_id=msg_id)

        bot.answerCallbackQuery(query_id)
    elif '/setdescription' == query_data:
        if chats[chat_id]['event_selected'] is not None:
            query_user_edit(chat_id, msg['from'], chats[chat_id]['event_selected'], 'description')
            bot.answerCallbackQuery(query_id)
        else:
            bot.answerCallbackQuery(query_id, "This event is no longer valid! 😣")
    elif '/setlocation' == query_data:
        if chats[chat_id]['event_selected'] is not None:
            query_user_edit(chat_id, msg['from'], chats[chat_id]['event_selected'], 'location')
            bot.answerCallbackQuery(query_id)
        else:
            bot.answerCallbackQuery(query_id, "This event is no longer valid! 😣")
    elif '/setdate' == query_data:
        if chats[chat_id]['event_selected'] is not None:
            query_user_edit(chat_id, msg['from'], chats[chat_id]['event_selected'], 'date')
            bot.answerCallbackQuery(query_id)
        else:
            bot.answerCallbackQuery(query_id, "This event is no longer valid! 😣")
    elif '/settime' == query_data:
        if chats[chat_id]['event_selected'] is not None:
            query_user_edit(chat_id, msg['from'], chats[chat_id]['event_selected'], 'time')
            bot.answerCallbackQuery(query_id)
        else:
            bot.answerCallbackQuery(query_id, "This event is no longer valid! 😣")
    elif '/delete' in query_data:
        text = ""

        if chats[chat_id]['event_selected'] is not None:
            planner.delete(chat_id, chats[chat_id]['event_selected'])
            text = "Aww... 😿"
        elif len(query_data.split(' ', 1)) == 2:
            planner.delete(chat_id, int(query_data.split(' ', 1)[1]))
            text = "Aww... 😿"

        bot.answerCallbackQuery(query_id, text=text)
        show_events(chat_id, '/delete', msg_id=msg_id)             # Refresh UI
    elif query_data == '/menu':
        show_menu(chat_id, msg['from'], msg_id=msg_id)
        bot.answerCallbackQuery(query_id)


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(0.5)
