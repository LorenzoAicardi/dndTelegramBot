import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from . import initialMenu
from classes import Monster

DM, DMMENU = range(2)


def activeCamp():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("^Done$"), playerMenu)],
        states={
            DMMENU: [MessageHandler(Filters.regex("^Done$"), dmMenu), MessageHandler(Filters.text, dmMenu)],
            DM: [MessageHandler(Filters.regex("^Add item to player...|Remove item from player...|"
                                              "Add spell to player...|Damage player|Heal player$"), choosePlayer),
                 MessageHandler(Filters.regex("^Add item to player...|"
                                              "Remove item from player...|Add spell to player...$"), chooseItem),
                 MessageHandler(Filters.text, choice)]
        },
        fallbacks=[],
        per_user=False,
        per_chat=True
    )


def playerMenu(update: Update, context: CallbackContext) -> int:
    if update.message.from_user.username in context.user_data["dm"]:
        return DMMENU


def dmMenu(update: Update, context: CallbackContext) -> int:
    menu = [[KeyboardButton("Begin combat")],
            [KeyboardButton("Add item to player...")],
            [KeyboardButton("Remove item from player...")],
            [KeyboardButton("Add spell to player...")],
            [KeyboardButton("Damage player")],
            [KeyboardButton("Heal player")]]
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=menu)
    return DM


def choosePlayer(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.")
    context.user_data["dmChoice"] = update.message.text
    return DM


def chooseItem(update: Update, context: CallbackContext):
    context.user_data["chosenPlayer"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the item/spell to add/remove.")
    return DM


def choice(update: Update, context: CallbackContext):
    if context.user_data["dmChoice"] == "Add item to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        item = update.message.text
        context.user_data[chosenPlayer + "char"].addItem(item)
        return DMMENU
    elif context.user_data["dmChoice"] == "Remove item to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        item = update.message.text
        context.user_data[chosenPlayer + "char"].rmItem(item)
        return DMMENU
    elif context.user_data["dmChoice"] == "Add spell to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        spell = update.message.text
        context.user_data[chosenPlayer + "char"].addSpell(spell)
        return DMMENU
