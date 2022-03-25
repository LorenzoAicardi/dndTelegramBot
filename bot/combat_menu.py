from telegram import *
from telegram.ext import *
import os


def combat():
    return ConversationHandler(
        entry_points=[CommandHandler("", surpriseCalc)]
    )


def surpriseCalc(update: Update, context: CallbackContext):