import time
import telepot
import nltk
from telepot.loop import MessageLoop
from constants import *

state = None
user = None
plan = dict()


def handle(msg):
    global state, user

    chat_id = msg['chat']['id']
    text = msg['text']
    tokens = nltk.word_tokenize(text)
    command = tokens[0]

    print('Got command: %s' % command)
    # print(msg)

    if state is None and command == '/new':
        state = NEW_PLAN_DESC
        user = msg['from']['id']
        send_msg = 'What is the event? Reply using command "/what".'
    elif state == NEW_PLAN_DESC and msg['from']['id'] == user and command == '/what':
        state = NEW_PLAN_LOC
        plan["desc"] = ' '.join(tokens[1:])
        send_msg = 'Where is the event? Reply using command "/where".'
    elif state == NEW_PLAN_LOC and msg['from']['id'] == user and command == '/where':
        state = NEW_PLAN_TIME
        plan["place"] = ' '.join(tokens[1:])
        send_msg = 'When is the event? Reply using command "/when".'
    elif state == NEW_PLAN_TIME and msg['from']['id'] == user and command == '/when':
        state = None    # Reset state
        plan["time"] = ' '.join(tokens[1:])
        send_msg = 'desc: {}\nplace: {}\ntime: {}'.format(plan["desc"], plan["place"], plan["time"])

    bot.sendMessage(chat_id, send_msg)


TOKEN = "491299803:AAFHXQRRI7BzNIrCUdoW2p80nt0gHFo5A_w"

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(1)
