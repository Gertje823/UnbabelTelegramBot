import requests
import time
import telegram
from telegram.ext import Updater, CommandHandler
from datetime import datetime
import json

# load config.json
with open('config.json', 'r') as f:
    config = json.load(f)

sessionid = config['UNBABEL']['SESSIONID']
username = config['UNBABEL']['USERNAME']
chat_id = config['TELEGRAM']['CHAT_ID']
api_key = config['TELEGRAM']['API_KEY']
minimum = config['PREFERENCES']['MINIMUM']
print(f'Minimum is set to {minimum}')

global cookies
cookies = {'sessionid': sessionid}

old_tasks = 0


updater = Updater(token=api_key)
dispatcher = updater.dispatcher


def get_balance(bot, update):
    url = f'https://unbabel.com/api/v1/user/{username}'
    r = requests.get(url, cookies=cookies)
    data = r.json()
    balance = data['balance']
    msg = f'Account balance: ${balance}'
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg)


def get_pending(bot, update):
    url = f'https://unbabel.com/api/v1/user/{username}'
    r = requests.get(url, cookies=cookies)
    data = r.json()
    cashout_history = data['cashout_history']
    amount = 0
    for cashout in cashout_history:
        status = cashout['status']
        if status == 'pending':
            amount1 = int(cashout['amount'])
            amount = amount + amount1

    msg = f'Total amount pending: ${amount}'
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg)


# get total earned
def get_total_earned(bot, update):
    url = f'https://unbabel.com/api/v1/user/{username}'
    r = requests.get(url, cookies=cookies)
    data = r.json()
    total_income = data['total_income']
    tasks_done = data['tasks_done']
    msg = f'Total earned: ${total_income} \nTotal tasks done: {tasks_done}'
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg)


# get tasks
def get_tasks(bot, update):
    url = 'https://unbabel.com/api/v1/available_tasks'
    r = requests.get(url, cookies=cookies)
    data = r.json()
    paid = data['paid']
    if not paid:
        bot.send_message(chat_id=update.message.chat_id,
                         text='You\'re not able to do paid tasks')
    else:
        for tasks in paid:
            task = tasks['tasks_available']
            if 0 is task:
                bot.send_message(chat_id=update.message.chat_id, text='No tasks')
            else:
                source_lang = tasks['language_pair']['source_language']['name']
                target_lang = tasks['language_pair']['target_language']['name']
                hourly_rate = tasks['language_pair']['hourly_rate']
                hourly_rate = round(hourly_rate / 100, 2)

                print(str(datetime.now()), 'Tasks available:', task, 'from', source_lang, 'to', target_lang, '\n')
                # send telegram msg
                msg = f'Tasks available: {task}, from  {source_lang} to {target_lang} \nHourly rate: ${hourly_rate}'
                bot.send_message(chat_id=update.message.chat_id,
                                 text=msg)

def set_minimum(bot, update):
    msg = update.message.text
    if msg == '/set_minimum':
        text = f'Please type a number after the command'
        turl = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text}'
        requests.get(turl)
    else:
        global minimum
        minimum = msg.replace('/set_minimum ', '')
        try:
            minimum = int(minimum)
            config['PREFERENCES']['MINIMUM'] = minimum
            with open("config.json", "w") as jsonFile:
                json.dump(config, jsonFile)

            print(str(datetime.now()), f'minimum set to {minimum}')
            text = f'You get a notification if there are more than {minimum} tasks'
            turl = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text}'
            requests.get(turl)      
        except ValueError:
            print(error)
            text = f'Please type a number after the command'
            turl = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={text}'
            requests.get(turl)
        
        



dispatcher.add_handler(CommandHandler('tasks', get_tasks))
dispatcher.add_handler(CommandHandler('set_minimum', set_minimum))
dispatcher.add_handler(CommandHandler('balance', get_balance))
dispatcher.add_handler(CommandHandler('pending', get_pending))
dispatcher.add_handler(CommandHandler('total_earned', get_total_earned))
updater.start_polling(clean=True)

while True:
    url = 'https://unbabel.com/api/v1/available_tasks'
    r = requests.get(url, cookies=cookies)
    data = r.json()
    paid = data['paid']
    if not paid:
        print(str(datetime.now()), 'Not allowed to do paid tasks')
    else:
        for tasks in paid:
            task = tasks['tasks_available']
            source_lang = tasks['language_pair']['source_language']['name']
            target_lang = tasks['language_pair']['target_language']['name']
            hourly_rate = tasks['language_pair']['hourly_rate']
            hourly_rate = round(hourly_rate / 100, 2)
            if old_tasks < task:
                if int(minimum) < task:
                    print(str(datetime.now()), 'Tasks available:', task, 'from', source_lang, 'to', target_lang, '\n')
                    # send telegram msg
                    msg = f'Tasks available: {task}, from {source_lang} to {target_lang} \nHourly rate: ${hourly_rate}'
                    turl = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&text={msg}'
                    requests.get(turl)
                else:
                    print(str(datetime.now()), f'There are {task} tasks available but it is not more than {minimum}')
            else: print(str(datetime.now()), f'Tasks available: {task}, from {source_lang} to {target_lang}')
            old_tasks = task
    time.sleep(600)
