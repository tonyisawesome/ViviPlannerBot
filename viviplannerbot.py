import time
import telepot
import nltk
from telepot.loop import MessageLoop
from constants import *

user_req = None
chat_state = dict()
plan = dict()


def handle(msg):
    global chat_state, user_req, plan

    chat_id = msg['chat']['id']
    text = msg['text']
    user = msg['from']['username']
    tokens = nltk.word_tokenize(text)
    command = tokens[0]
    send_msg = ""

    print('Got command: %s' % command)
    print(msg)

    if chat_id not in chat_state:
        chat_state[chat_id] = None

    if chat_state[chat_id] is None and command == '/new':
        chat_state[chat_id] = NEW_PLAN_DESC
        user_req = user
        send_msg = '{}\nWhat is the event? Reply using command: /what.'.format("@" + user_req)
    elif chat_state[chat_id] == NEW_PLAN_DESC and user_req == user and command == '/what':
        chat_state[chat_id] = NEW_PLAN_LOC
        plan["desc"] = ' '.join(tokens[1:])
        send_msg = '{}\nWhere is the event? Reply using command: /where.'.format("@" + user_req)
    elif chat_state[chat_id] == NEW_PLAN_LOC and user_req == user and command == '/where':
        chat_state[chat_id] = NEW_PLAN_TIME
        plan["place"] = ' '.join(tokens[1:])
        send_msg = '{}\nWhen is the event? Reply using command: /when.'.format("@" + user_req)
    elif chat_state[chat_id] == NEW_PLAN_TIME and user_req == user and command == '/when':
        chat_state[chat_id] = None    # Reset state
        plan["time"] = ' '.join(tokens[1:])
        send_msg = 'desc: {}\nplace: {}\ntime: {}'.format(plan["desc"], plan["place"], plan["time"])

    if send_msg:
        bot.sendMessage(chat_id, send_msg)


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while True:
    time.sleep(1)
