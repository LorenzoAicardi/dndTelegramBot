from telegram import *
from telegram.ext import *
import os

# import characterCreation

NEWCAMPAIGN, LOADCAMPAIGN, NUMPLAYERS, CHARCREATION = range(4)

cwd = os.getcwd()


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEWCAMPAIGN: [MessageHandler(Filters.regex('^New campaign$'), newCampaign)],
            LOADCAMPAIGN: [MessageHandler(Filters.regex('^Load campaign$'), loadCampaign)],
            NUMPLAYERS: [MessageHandler(Filters.text, numberOfPlayers)],
            CHARCREATION: [MessageHandler(Filters.text, charCreation)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)]
    )


def start(update: Update, context: CallbackContext) -> int:
    startingMenu = [[InlineKeyboardButton("New campaign", callback_data="New campaign")], [InlineKeyboardButton("Load campaign", callback_data="Load campaign")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose whether you want to start a new campaign"
                                                                    "or load an older one.",
                             reply_markup=InlineKeyboardMarkup(startingMenu, one_time_keyboard=True))
    #if "New campaign" in update.message.text:
        #print('here!') #Doesn't get here!
    #    return NEWCAMPAIGN
    #if "Load campaign" in update.message.text:
    #    return LOADCAMPAIGN


def quitCampaign(update: Update, context: CallbackContext) -> int:
    # insertstufftosavegamehere: se ho aperto una partita, la salvo, altrimenti non faccio nulla.
    # if the game has been saved:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your game has been saved!  Press /start to "
                                                                    "load a new game.")
    return ConversationHandler.END


def newCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, a new campaign! Choose the number of "
                                                                    "players that want to start this campaign. "
                                                                    "Remember "
                                                                    "that more players will always be able to join "
                                                                    "later. What should we name it?")
    return NUMPLAYERS


def numberOfPlayers(update: Update, context: CallbackContext) -> int:
    path = cwd + "/campaigns"
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    open(update.message.text + ".json", "x")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your campaign has been created successfully!"
                                                                    "Now input the number of players that want"
                                                                    "to play (except the DM). Remember, newer players"
                                                                    "can join the campaign once it has started.")
    return CHARCREATION


def charCreation(update: Update, context: CallbackContext):
    try:
        val = int(update.message.text)
    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Input is not a number. Try again please")
        return CHARCREATION
    return ConversationHandler(  # creates a new character n times, where n is context.text
        entry_points=[MessageHandler(Filters.text)],
        states={

        }
    )


def loadCampaign(update: Update, context: CallbackContext) -> int:
    if "Load campaign" in update.message.text:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Select the campaign to load.")
