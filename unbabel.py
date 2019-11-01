import requests
import json
import re
from decimal import Decimal
import time
import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
from datetime import datetime
def parseCookieFile(cookiefile):
    """Parse a cookies.txt file and return a dictionary of key value pairs
    compatible with requests."""

    cookies = {}
    with open (cookiefile, 'r') as fp:
        for line in fp:
            if not re.match(r'^\#', line):
                lineFields = line.strip().split('\t')
                cookies[lineFields[5]] = lineFields[6]
    return cookies


chat_id = 'chat_id_Telegram'
username= 'Usernam_Unbabel'
api_key = 'Telegram:Token'
old_tasks = 0/
updater = Updater(token=api_key)
dispatcher = updater.dispatcher

def get_balance(bot, update):
    url = 'https://unbabel.com/api/v1/user/{}'.format(username)
    cookies = parseCookieFile('cookies.txt')
    r = requests.get(url, cookies=cookies)
    data = r.json()
    balance = data['balance']
    msg = 'Account balance: ${}'.format(balance)
    bot.send_message(chat_id=update.message.chat_id,
                         text=msg)
    
def get_pending(bot, update):
    url = 'https://unbabel.com/api/v1/user/{}'.format(username)
    cookies = parseCookieFile('cookies.txt')
    r = requests.get(url, cookies=cookies)
    data = r.json()
    cashout_history = data['cashout_history']
    amount = int(0)
    for cashout in cashout_history:
        status = cashout['status']
        cash_type = cashout['type']
        if status == 'pending':
            amount1 = int(cashout['amount'])
            print('$',amount1)
            amount = amount + amount1
            
            

    msg = 'Total amount pending: ${}'.format(amount)
    bot.send_message(chat_id=update.message.chat_id,
                         text=msg)

#get total earned
def get_total(bot, update):
    url = 'https://unbabel.com/api/v1/user/{}'.format(username)
    cookies = parseCookieFile('cookies.txt')
    r = requests.get(url, cookies=cookies)
    data = r.json()
    total_income = data['total_income']
    tasks_done = data['tasks_done']
    print(total_income)
    msg = 'Total earned: ${} \nTotal tasks done: {}'.format(total_income, tasks_done)
    bot.send_message(chat_id=update.message.chat_id,
                         text=msg)
	
#get tasks 
def get_tasks(bot, update):
    
    url = 'https://unbabel.com/api/v1/available_tasks'
    cookies = parseCookieFile('cookies.txt')
    r = requests.get(url, cookies=cookies)
    data = r.json()
    paid = data['paid']
    if not paid:
        print('You are not able to do paid tasks')
    else:
        for tasks in paid:
            task = tasks['tasks_available']
            print(task)
            if 0 is task:
                bot.send_message(chat_id=update.message.chat_id, text='No tasks')
            else:
                lang = tasks['language_pair']['source_language']['name']
                lang2 = tasks['language_pair']['target_language']['name']
                hourly_rate = tasks['language_pair']['hourly_rate']
                hourly_rate = hourly_rate/100
                hourly_rate = round(hourly_rate, 2)
                
                print(str(datetime.now()), 'Tasks available:', task, 'from', lang, 'to', lang2, '\n')
                #send telegram msg
                msg = 'Tasks available: {}, from  {} to {} \n Hourly rate: ${}'.format(task, lang, lang2, hourly_rate)
                bot.send_message(chat_id=update.message.chat_id,
                         text=msg)
                            
dispatcher.add_handler(CommandHandler('get', get_tasks))
dispatcher.add_handler(CommandHandler('balance', get_balance))
dispatcher.add_handler(CommandHandler('pending', get_pending))
dispatcher.add_handler(CommandHandler('earned', get_total))
updater.start_polling(clean=True)                

while True:    
    url = 'https://unbabel.com/api/v1/available_tasks'
    cookies = parseCookieFile('cookies.txt')
    r = requests.get(url, cookies=cookies)
    data = r.json()
    paid = data['paid']
    if not paid:
        print(str(datetime.now()), 'no tasks')
    else:
        for tasks in paid:
            task = tasks['tasks_available']
            lang = tasks['language_pair']['source_language']['name']
            lang2 = tasks['language_pair']['target_language']['name']
            hourly_rate = tasks['language_pair']['hourly_rate']
            hourly_rate = hourly_rate/100
            hourly_rate = round(hourly_rate, 2)
            if old_tasks < task:
                print(str(datetime.now()), 'Tasks available:', task, 'from', lang, 'to', lang2, '\n')
                #send telegram msg
                msg = 'Tasks available: {}, from {} to {} \n Hourly rate: ${}'.format(task, lang, lang2, hourly_rate)
                turl = 'https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(api_key, chat_id, msg)
                requests.get(turl)
            else:
                print(str(datetime.now()), 'There are no new tasks')
            old_tasks = task
    time.sleep(600)




