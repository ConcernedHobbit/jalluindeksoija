import logging
from math import ceil
import sys
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from jalluindex import Jalluindex

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

jalluindex = Jalluindex()

def commands(update: Update, context: CallbackContext):
    update.message.reply_text(
        f'Jalluindex: {jalluindex.index}€\n'
         'Commands:\n'
         '/ji [amount]\n'
         '/thank [amount]\n'
    )

def index(update: Update, context: CallbackContext):
    args = update.message.text.split(' ')

    amount = 1
    if len(args) > 1:
        try:
            amount = int(args[1])
        except:
            logger.info(f'{update.message.from_user.username} tried to get index for "{args[1]}"')

    message = f'Jalluindex: {jalluindex.index:.2f}€'

    if amount > 1:
        euros = jalluindex.index * amount
        message = f'{amount} JI = {euros:.2f}€'

    update.message.reply_text(message)

def thank(update: Update, context: CallbackContext):
    args = update.message.text.split(' ')
    
    amount = 5
    if len(args) > 1:
        try:
            amount = int(args[1])
        except:
            logger.info(f'{update.message.from_user.username} tried to get thanks for "{args[1]}"')

    budget = jalluindex.index * ceil(amount / 3)

    update.message.reply_text(
        f'Budget for {amount}: {budget}€'
    )

def main():
    if not 'TG_TOKEN' in os.environ:
        logger.error('TG_TOKEN must be present in environment variables')
        sys.exit(1)

    TG_TOKEN = os.environ['TG_TOKEN']

    updater = Updater(token=TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler(['start', 'help'], commands))
    dispatcher.add_handler(CommandHandler('ji', index))
    dispatcher.add_handler(CommandHandler('thank', thank))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()