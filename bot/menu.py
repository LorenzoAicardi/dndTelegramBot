from telegram import *
from telegram.ext import *
import os

# import characterCreation

CAMPAIGN, NUMPLAYERS, CHARCREATION = range(3)

dir = os.getcwd()


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CAMPAIGN: [MessageHandler(Filters.regex('^New campaign$'), newCampaign),
                       MessageHandler(Filters.regex('^Load campaign$'), loadCampaign)],
            NUMPLAYERS: [MessageHandler(Filters.text, numberOfPlayers)],
            CHARCREATION: [MessageHandler(Filters.text, charCreation)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)]
    )


def start(update: Update, context: CallbackContext) -> int:
    startingMenu = [[KeyboardButton("New campaign")], [KeyboardButton("Load campaign")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose whether you want to start a new campaign"
                                                                    "or load an older one.",
                             reply_markup=ReplyKeyboardMarkup(startingMenu, one_time_keyboard=True))
    return CAMPAIGN


def quitCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your game has been saved!  Press /start to "
                                                                    "load a new game.")
    return ConversationHandler.END


def loadCampaign(update: Update, context: CallbackContext) -> int:
    path = dir + "/campaigns"
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
        replyK.append([KeyboardButton(cmp[:len(cmp)-5])])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the campaign you want to load!",
                             reply_markup=ReplyKeyboardMarkup(replyK, one_time_keyboard=True))
    return CHARCREATION

    # TODO: should be a RETURN GAMESTATE or whatever I decide to call the menu when the game starts


def newCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, a new campaign! Choose the number of "
                                                                    "players that want to start this campaign. "
                                                                    "Remember "
                                                                    "that more players will always be able to join "
                                                                    "later. What should we name it?")
    return NUMPLAYERS


def numberOfPlayers(update: Update, context: CallbackContext) -> int:
    path = dir + "/campaigns"
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

