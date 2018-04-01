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
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def announceBlock(bot, update, message):
    """Called when a block is found to announce it."""
    update.message.reply_text(message)

def checkBlock(bot, job):
    """Check for a recent blocks and uncles"""
    #logger.info("checkBlock")
    try:
        payload = { 'module': 'account',
                    'action': 'getminedblocks',
                    'address': address,
                    'page': '1',
                    'offset': '1',
                    'type': 'blocks',
                    'apikey': secrets.etherscan_token }
        #message = str("Noobpool hit a block!\r\n#{} was found at {} UTC.  {}").format(block, date.strftime('%Y-%m-%d %H:%M:%S'), pleasantry())
        # we need to pass back block and time data from the query function -- oops
        message = str("Noobpool hit a block!  {}").format(pleasantry())
        request = queryEtherscan(payload)
        if checkLast(request):
            announceBlock(message, job.context)

        payload = { 'module': 'account',
                    'action': 'getminedblocks',
                    'address': address,
                    'page': '1',
                    'offset': '1',
                    'type': 'uncles',
                    'apikey': secrets.etherscan_token }
        #message = str("Noobpool hit an uncle!\r\n#{} was found at {} UTC.  {}").format(block, date.strftime('%Y-%m-%d %H:%M:%S'), pleasantry())
        message = str("Noobpool hit an uncle!  {}").format(pleasantry())
        request = queryEtherscan(payload)
        if checkLast(request):
            announceBlock(message, job.context)

    except Exception as e:
        logger.error(repr(e))


def queryEtherscan(payload):
    """Query the etherscan API"""
    return requests.get('https://api.etherscan.io/api', params=payload).json()['result'][0]

def checkLast(last):
    """Check recent blocks for freshness, return true if <1m old""" 
    block, date = last['blockNumber'], datetime.datetime.fromtimestamp(int(last['timeStamp']))
    if (datetime.datetime.utcnow()-date <= datetime.timedelta(seconds=60)):
        return True
    else:
        return False

def scheduleJob(bot, update, args, job_queue):
    """Add a job to the job queue"""
    #in seconds
    interval = 60
    if not job_queue.jobs(): # Only add a job if the queue is empty.
        job = job_queue.run_repeating(checkBlock, interval, context=update)
        logger.info("added job")

    
def fetchMinerstats(wallet):
    """Fetch Miner statistics with an API call to noobpool."""
    url = str("http://www.noobpool.com/api/accounts/{}").format(wallet)
    result = requests.get(url).json()
    workers = result['workersOnline']
    hashrate = result['currentHashrate']/1000000.0
    #roundshare = result['roundShares']
    #TODO: figure out roundShare calculation.
    return str("Statistics for {}\r\n{} workers mining at {}MH/s. {}").format(wallet, workers, hashrate, pleasantry())
	
def stats(bot, update, args):
    """Prompt for ether wallet if not supplied"""
    if len(args) == 0:
        update.message.reply_text("Which wallet would you like stats for?",reply_markup=ForceReply(force_reply=True))
    else:
        try:
            update.message.reply_text(fetchMinerstats(args[0]))
        except IndexError as e:
            logger.error(repr(e))

def getstats(bot, update):
    """Check for reply, request noobpool statistics"""
    try:
        update.message.reply_text(fetchMinerstats(update.message.text))
    except Exception as e:
        logger.error(repr(e))

def pleasantry():
    pleasantries = ["Cheers!", "Happy Hashing!", "Mine On!", "Cheers Miners!", "Cheers Noobs!", "Keep Mining Noobs!", "Hoppers Begone!"]
    return choice(pleasantries)
    
def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(secrets.telegram_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", scheduleJob, pass_args=True, pass_job_queue=True))
    dp.add_handler(CommandHandler("stats", stats, pass_args=True))
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
