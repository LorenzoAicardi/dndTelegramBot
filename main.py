import telegram
import telegram.ext
import logging
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from bot import starting_menu
from bot.starting_menu import start, newCampaign

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    updater = Updater("5255908305:AAGMqYJEPUhbyUF-Ms_bgtVRHApla6hIDls")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(starting_menu.start_cmd())
    dispatcher.add_handler(combat_menu.combat())

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
