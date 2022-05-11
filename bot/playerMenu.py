import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from classes.JSONEncoder import MyEncoder
from . import charCreationMenu
from classes import Monster

PLAYERMENU=1

def playerMenu():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaign', menu)],
        states={
            PLAYERMENU: [MessageHandler(Filters.text, playerMenu)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)]
    )


def menu(update: Update, context: CallbackContext):
    pass


def quitCampaign(update: Update, context: CallbackContext):
    pass
