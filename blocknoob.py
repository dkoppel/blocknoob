#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Noobpool Telegram bot - Please send donations to the EFF
(or to us if you really really want.  ETH: 9be66956315c53d129f9805a561227480723ca15 BTC: 195CxNXc5XS7uLxi9Fq6vAW4kLnTjiod7R )
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ForceReply
from random import choice
import logging
import requests
import datetime
import secrets 

#Noobpool miner.
address = '0xd5bBb4264b70ca4F58C45d27B9D7E11190754a54'

#Enable logging.
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Callbacks for handlers.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Welcome!')
    
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def fetchLastblock():
    """Fetch last ether block mined by noobpool."""
    payload = { 'module': 'account', 'action': 'getminedblocks', 'address': address, 'blocktype': 'blocks', 'apikey': secrets.etherscan_token }
    last = requests.get('https://api.etherscan.io/api', params=payload).json()['result'][0]
    block, date = last['blockNumber'], datetime.datetime.fromtimestamp(int(last['timeStamp']))
    return str("Most recent noobpool block #{} was found at {}.  {}").format(block, date.strftime('%Y-%m-%d %H:%M:%S'), pleasantry())

def lastblock(bot, update):
    """Send information about the last block mined."""
    message = fetchLastblock()
    update.message.reply_text(message)

def fetchMinerstats(wallet):
    """Fetch Miner statistics with an API call to noobpool."""
    url = str("http://www.noobpool.com/api/accounts/{}").format(wallet)
    result = requests.get(url).json()
    workers = result['workersOnline']
    hashrate = result['currentHashrate']/1000000.0
    #roundshare = result['roundShares']
    #TODO: figure out roundShare calculation.
    return str("Statistics for {}\r\n{} workers mining at {}MH/s. {}").format(wallet, workers, hashrate, pleasantry())
	
def stats(bot, update):
    """Prompt for ether wallet TODO inline or /stats@wallet"""
    update.message.reply_text("Which wallet would you like stats for?",reply_markup=ForceReply(force_reply=True))

def getstats(bot, update):
    """Check for reply, request noobpool statistics"""
    try:
        update.message.reply_text(fetchMinerstats(update.message.text))
    except Error as e:
        logger.error(e)

def pleasantry():
    pleasantries = ["Cheers!", "Happy Hashing!", "Mine On!", "Cheers Miners!", "Cheers Noobs!"]
    return choice(pleasantries)
    
def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(secrets.telegram_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("lastblock", lastblock))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(MessageHandler(Filters.reply, getstats))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
