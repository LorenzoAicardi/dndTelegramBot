import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from . import initialMenu
from classes import Monster

equipLoop = "^Mace$|^Warhammer$|^Scale Mail$|^Leather Armor$|^Chain Mail$|^Leather Armor$|^Longbow$|^Martial " \
            "Weapon$|^Shield$|^Martial Weapon$|^Light Crossbow$|^Handaxe$|^Dungeoneer's Pack$|^Explorer's " \
            "Pack$|^Rapier$|^Shortbow$|^Shortsword$||^Burglar's Pack$|^Dagger$|^Thieves' " \
            "Tools$|^Quarterstaff$|^Component Pouch$|^Arcane Focus$|^Scholar's Pack$|^Spellbook$"

CAMPAIGN, NEWCAMP, CHARCREATION, SETNAME, SETEQUIP, KEEPEQUIP = range(6)

cwd = os.getcwd()


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(Filters.regex("^Done$"), start)],
        states={
            CAMPAIGN: [MessageHandler(Filters.regex('^New campaign$'), newCampaign),
                       MessageHandler(Filters.regex('^Load campaign$'), loadCampaign)],
            NEWCAMP: [initialMenu.createChar()],
            # CAMPMENU: [MessageHandler(Filters.regex("^Done$"), playerMenu)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)],
        per_user=False,
        per_chat=True
    )


def start(update: Update, context: CallbackContext) -> int:
    startingMenu = [[KeyboardButton("New campaign")], [KeyboardButton("Load campaign")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose whether you want to start a new campaign"
                                                                    "or load an older one.",
                             reply_markup=ReplyKeyboardMarkup(startingMenu, one_time_keyboard=True))
    return CAMPAIGN


def newCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, a new campaign! What should we name it?")
    return ConversationHandler.END

############LOAD CAMPAIGN##############


def loadCampaign(update: Update, context: CallbackContext) -> int:
    path = cwd + "/campaigns"
    if not os.path.isdir(path):
        startingMenu = [[KeyboardButton("New campaign")], [KeyboardButton("Load campaign")]]
        context.bot.send_message(chat_id=update.effective_chat.id, text="It appears you haven't saved a campaign yet. "
                                                                        "Create a new one!",
                                 reply_markup=ReplyKeyboardMarkup(startingMenu, one_time_keyboard=True))
        return CAMPAIGN
    os.chdir(path)
    campaignList = os.listdir()
    replyK = []
    for cmp in campaignList:
        replyK.append([KeyboardButton(cmp[:len(cmp) - 5])])  # last five characters are ".json"
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the campaign you want to load!",
                             reply_markup=ReplyKeyboardMarkup(replyK, one_time_keyboard=True))
    return ConversationHandler.END


def quitCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you next time!")
    return ConversationHandler.END

    # TODO: should be a RETURN GAMESTATE or whatever I decide to call the menu when the game starts

######################PLAYER MENU#########################


# def playerMenu(update: Update, context: CallbackContext):
