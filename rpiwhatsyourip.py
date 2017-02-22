#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
MIT License

Copyright (c) 2017 Daniel Hernández Pancorbo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import ConfigParser
import argparse
import datetime
import logging
import os
import socket
import sys
import threading
import time

import telebot
import tweepy

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help='Increase verbosity level', action='store_true')
arg_grp1 = parser.add_argument_group(title='Bots', description='Parameters required for bots to activate. Each bot '
                                                               'needs specific configuration')
arg_grp1.add_argument('--telegram', help='Enable Telegram bot', action='store_true')
arg_grp1.add_argument('--twitter', help='Enable Twitter bot', action='store_true')
parser.add_argument('--nrt', help='Do not tweet the current IP if it\'s the same as the one in the last '
                                  'tweet. Will be saved in the config file', action='store_true')
args = parser.parse_args()

settings = ConfigParser.RawConfigParser()
if not os.path.exists('./rpiwhatsyourip.cfg'):
    settings_file = open('./rpiwhatsyourip.cfg', mode='w')
    settings.add_section('Telegram')
    settings.set('Telegram', 'bot_token', 'INSERT_YOUR_TOKEN_HERE')
    settings.set('Telegram', 'reply_message', 'Your Raspberry IP is {rpiIP}')
    settings.add_section('Twitter')
    settings.set('Twitter', 'consumer_key', 'YOUR_CONSUMER_KEY')
    settings.set('Twitter', 'consumer_secret', 'YOUR_CONSUMER_SECRET')
    settings.set('Twitter', 'access_token', 'YOUR_ACCESS_TOKEN')
    settings.set('Twitter', 'access_token_secret', 'YOUR_ACCESS_TOKEN_SECRET')
    settings.set('Twitter', 'tweet', '@yourUsername my IP is {rpiIP}')
    settings.set('Twitter', 'last_tweet_ip', '127.0.0.1')
    settings.write(settings_file)
    settings_file.close()
    logging.debug('Config file created')
    sys.exit('A config file has been created for you. Edit \"rpiwhatsyourip.cfg\" with your data.')

settings.read('rpiwhatsyourip.cfg')


def get_safe_config(section):
    settings_dict = {}
    options = settings.options(section)
    for option in options:
        try:
            settings_dict[option] = settings.get(section, option)
            if settings_dict[option] == -1:
                logging.debug('setting \"%s\" skipped' % option)
        except:
            logging.error('setting \"%s\" not exists' % option)
            settings_dict[option] = None
            sys.exit('Your config file was corrupt, delete it and let the program rebuild a new one for you')
    return settings_dict


saved_telegram = get_safe_config('Telegram')
saved_twitter = get_safe_config('Twitter')
last_ip = str(get_safe_config('Twitter')['last_tweet_ip'])


def get_user_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]  # retrieve the IP used in that socket
        # return  socket.gethostbyname(socket.gethostname()) # not working on most Linux servers
        # We can also execute 'hostname -I' and get that command output.
    except:
        return 'No.Valid.IP'


if args.telegram:
    bot = telebot.TeleBot(
        str(get_safe_config('Telegram')['bot_token']))
    telegram_updt = 0

if args.twitter:
    twitter_auth = tweepy.OAuthHandler(str(get_safe_config('Twitter')['consumer_key']),
                                       str(get_safe_config('Twitter')['consumer_secret']))
    twitter_auth.set_access_token(str(get_safe_config('Twitter')['access_token']),
                                  str(get_safe_config('Twitter')['access_token_secret']))
    twitter_api = tweepy.API(twitter_auth)


def main():
    try:
        if args.debug:
            logging.basicConfig(filename='rpiwhatsyourip.log', level=logging.DEBUG,
                                format='[DEBUG] %(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %I:%M:%S')
        else:
            logging.basicConfig(filename='rpiwhatsyourip.log', level=logging.ERROR,
                                format='[ERROR] %(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %I:%M:%S')
        if not (args.telegram or args.twitter):
            sys.exit('You must activate one bot! Use \"python rpiwhatsyourbot.py --help\" for more information')
        if args.twitter:
            check_ip_change()
        changes_saver()
        while True:
            try:
                if args.telegram:
                    bot.polling()
            except Exception as ex:
                logging.error(ex)
                time.sleep(20)  # time to pray to get the fail fixed...
    except Exception as ex:
        logging.error(ex)


if args.telegram:
    @bot.message_handler(commands=['yourip'])
    def bot_reply_ip(message):  # sometimes the server sends twice our update, that's why we'll ignore the first one
        global telegram_updt
        if telegram_updt > 0:
            bot.reply_to(message, text=get_safe_config('Telegram')['reply_message'].format(rpiIP=str(get_user_ip())))
        telegram_updt += 1


def check_ip_change():
    now_ip = str(get_user_ip())
    global last_ip
    if not args.nrt:
        if (now_ip != last_ip) and (now_ip != 'No.Valid.IP' and len(now_ip) >= 7):
            try:
                twitter_api.update_status('[' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d '
                                                                                                      '%H:%M:%S')
                                          + '] ' + str(get_safe_config('Twitter')['tweet']).format(rpiIP=now_ip))
            except Exception as ex:
                logging.error(ex)
            last_ip = now_ip
            settings.set('Twitter', 'last_tweet_ip', str(now_ip))
    elif (now_ip != last_ip) and (now_ip != 'No.Valid.IP' and len(now_ip) >= 7):
        try:
            twitter_api.update_status('[' + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') +
                                      '] ' + str(get_safe_config('Twitter')['tweet']).format(rpiIP=now_ip))
        except Exception as ex:
            logging.error(ex)
        last_ip = now_ip
        settings.set('Twitter', 'last_tweet_ip', str(now_ip))
    else:
        logging.info('The current IP is equal to the last tweet IP. No tweet has been posted.')
    threading.Timer(40, check_ip_change).start()


def changes_saver():
    settingsfile = open('./rpiwhatsyourip.cfg', mode='w')
    settings.write(settingsfile)
    settingsfile.close()
    threading.Timer(42, changes_saver).start()


if __name__ == '__main__':
    main()
