import random
from telegram import *
from telegram.ext import *
import os
menuRollback = "^d4|d8|d12|d20$" #Complete with all the messages that make you go back to the menu

MENU, ROLL, COMBAT, QUIT = range(3)


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler("start", menu)],
        states={
            MENU: [MessageHandler(Filters.regex(menuRollback), menu), MessageHandler(Filters.regex("^roll$"), roll)],
            ROLL: [MessageHandler(Filters.regex("^d4|d8|d12|d20$"), die)],
            #COMBAT: [MessageHandler(Filters.regex("^Move$"), move), MessageHandler(Filters.regex("^Action$"), action)]
        }
    )


def menu(update: Update, context: CallbackContext) -> int:
    actions = [KeyboardButton("Roll"), KeyboardButton("Combat"), KeyboardButton("Quit")]
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=actions)
    return MENU


def roll(update: Update, context: CallbackContext) -> int:
    dices = [KeyboardButton("d4"), KeyboardButton("d8"), KeyboardButton("d12"), KeyboardButton("d20")]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose a dice to roll!", reply_markup=dices)
    return ROLL


def die(update: Update, context: CallbackContext) -> int:
    dice = update.message.text
    res = 0
    match dice:
        case dice.__eq__("d4"):
            res = random.randint(1, 4)
        case dice.__eq__("d8"):
            res = random.randint(1, 8)
        case dice.__eq__("d12"):
            res = random.randint(1, 12)
        case dice.__eq__("d20"):
            res = random.randint(1, 20)
    context.bot.send_message(chat_id=update.effective_chat.id, text="You rolled a " + str(res) + "!")
    return MENU


def combat(update: Update, context: CallbackContext) -> int: #Tough: got to make sure that the player can only do them twice, or more if made possible by modifiers
    combatOptions = [KeyboardButton("Move"), KeyboardButton("Action")]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the action you want to take.",
                             reply_markup=combatOptions)
    return COMBAT

#def move(update: Update, context: CallbackContext) -> int:
