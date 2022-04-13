import telegram
from telegram import *
from telegram.ext import *
import os

# import characterCreation

CAMPAIGN, NEWCAMPAIGN, CHARCREATION = range(3)

dir = os.getcwd()


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CAMPAIGN: [MessageHandler(Filters.regex('^New campaign$'), newCampaign),
                       MessageHandler(Filters.regex('^Load campaign$'), loadCampaign)],
            NEWCAMPAIGN: [MessageHandler(Filters.text, setDM)],
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


def newCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, a new campaign! What should we name it?")
    return NEWCAMPAIGN


def setDM(update: Update, context: CallbackContext) -> int:
    path = dir + "/campaigns"
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    open(update.message.text + ".json", "x")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your campaign has been created successfully!"
                                                                    "The next user that writes a message will be "
                                                                    "the DM.")
    return CHARCREATION


def charCreation(update: Update, context: CallbackContext):
    dm = update.message.from_user
    players = update.message.new_chat_members()
    players.remove(dm)



############LOAD CAMPAIGN##############



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
        replyK.append([KeyboardButton(cmp[:len(cmp)-5])]) # last five characters are ".json"
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the campaign you want to load!",
                             reply_markup=ReplyKeyboardMarkup(replyK, one_time_keyboard=True))
    return ConversationHandler.END


def quitCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you next time!")
    return ConversationHandler.END

    # TODO: should be a RETURN GAMESTATE or whatever I decide to call the menu when the game starts


