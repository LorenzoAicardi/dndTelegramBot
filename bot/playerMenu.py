import json
from telegram import *
from telegram.ext import *
import os
from classes import Character, Dice, Statistics, Equipment
from classes.JSONEncoder import MyEncoder
from . import charCreationMenu
from classes import Monster

PLAYERMENU, ROLL = range(2)


def playerMenu():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaign', menu)],
        states={
            PLAYERMENU: [MessageHandler(Filters.text &
                                        ~Filters.regex("^Attack|Roll|Rest|Print stats|Print equipment|Quit$|Cast "
                                                       "spell..."), pMenu),
                         MessageHandler(Filters.regex("^Roll$"), roll),
                         MessageHandler(Filters.regex("^Print stats$"), printStats),
                         MessageHandler(Filters.regex("^Print equipment$"), printEquip)],
            ROLL: [MessageHandler(Filters.regex("^d4|d6|d8|d12|d20|d100$"), modifier),
                   MessageHandler(Filters.text & ~Filters.regex("^Roll$") &
                                  ~Filters.regex("^d4|d6|d8|d12|d20|d100$"), resolveDie)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)],
        per_chat=True,
        per_user=False
    )


# Only checking if the user is a player
def menu(update: Update, context: CallbackContext):  # NEED TO REPLACE USER DATA WITH CHAT DATA
    if update.message.from_user.id == context.chat_data["activeCampaign"]["dm"]:  # Players don't enter the chat.
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're the DM, not a player!")
        return ConversationHandler.END
    if context.bot_data["newCampaign"]:
        context.chat_data["activeCampaign"][update.message.from_user.username + "char"] = context.user_data["activeCampaign"][update.message.from_user.username + "char"]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write anything to pop up the player menus!")
    return PLAYERMENU


def pMenu(update: Update, context: CallbackContext):  # TODO: MAKE PLAYER EQUIP ARMOR; SO THAT HE GETS RIGHT ARMORCLASS
    keyboard = [[KeyboardButton("Attack")],  # Attack: get a combat menu. Available only if DM started combat.
                [KeyboardButton("Roll")],  # Roll: roll a dice of your choice.
                [KeyboardButton("Rest")],  # Rest: get the option for either a full rest or a short rest.
                [KeyboardButton("Print stats")],  # Prints stats.
                [KeyboardButton("Print equipment")],  # Prints equipment.
                [KeyboardButton(
                    "Quit")]]  # Quits campaign. Since per_user=false, essentially it will disable his character.
    if context.chat_data["activeCampaign"][update.message.from_user.username + "char"]._class == "cleric" \
            or context.chat_data["activeCampaign"][update.message.from_user.username + "char"]._class == "wizard":
        keyboard.append([KeyboardButton("Cast spell...")])  # Cast a spell. Only non-offensive spells out of combat.
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return PLAYERMENU


def roll(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("d4")],
                [KeyboardButton("d6")],
                [KeyboardButton("d8")],
                [KeyboardButton("d12")],
                [KeyboardButton("d20")],
                [KeyboardButton("d100")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose a die to throw.",
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return ROLL


def modifier(update: Update, context: CallbackContext):
    context.chat_data["chosenDie"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="If you want to use a modifier, "
                                                                    "write down the number."
                                                                    " Otherwise, type anything else.")
    return ROLL


# The mod could be an added value for a check, for example.
def resolveDie(update: Update, context: CallbackContext):
    mod = 0
    if update.message.text.isnumeric():
        mod = int(update.message.text)
    res = Dice.roll(context.chat_data["chosenDie"], mod)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The result of the die roll is: " + str(res))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def printStats(update: Update, context: CallbackContext):
    stats = Statistics.toString(context.chat_data["activeCampaign"][update.message.from_user.username + "char"].stats)
    context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data["activeCampaign"][update.message.from_user.username + "char"].name + "'s stats:\n"
                             + stats)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def printEquip(update: Update, context: CallbackContext):  # need to fix: won't work with wealth
    equip = Equipment.toString(context.chat_data["activeCampaign"][update.message.from_user.username + "char"].equipment)
    context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data["activeCampaign"][
                                                                        update.message.from_user.username + "char"].name + "'s equipment:\n"
                                                                    + equip)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def quitCampaign(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Goodbye " +
                                                                    update.message.from_user.username + "|")
    # context.chat_data["in_conversation"] = False
    return PLAYERMENU
