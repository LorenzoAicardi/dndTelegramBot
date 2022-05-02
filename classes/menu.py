import telegram
from telegram import *
from telegram.ext import *
import os

# import characterCreation
from classes import Character

CAMPAIGN, NEWCAMP, CHARCREATION, LOOP = range(4)

cwd = os.getcwd()


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CAMPAIGN: [MessageHandler(Filters.regex('^New campaign$'), newCampaign),
                       MessageHandler(Filters.regex('^Load campaign$'), loadCampaign)],
            NEWCAMP: [MessageHandler(Filters.text, setDM)],
            CHARCREATION: [MessageHandler(Filters.text, charCreation)],
            LOOP: [MessageHandler(Filters.text, creationLoop)]
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
    return NEWCAMP


def setDM(update: Update, context: CallbackContext) -> int:
    path = cwd + "/campaigns"
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    open(update.message.text + ".json", "x")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your campaign has been created successfully! "
                                                                    "The next user that writes a message will be "
                                                                    "the DM.")
    return CHARCREATION


def charCreation(update: Update, context: CallbackContext) -> int:
    global dm
    dm = update.message.from_user.username
    context.bot.send_message(chat_id=update.effective_chat.id, text=dm + " is the Dungeon Master for this campaign.")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Users in the chat that want to play the campaign"
                                                                    "may send a message here in chat. I will start"
                                                                    "a private conversation asking you to create the "
                                                                    "character, following my instructions.")
    return LOOP


def creationLoop(update: Update, context: CallbackContext):  # starts a private conversation with the user and creates char.
    context.bot.send_message(chat_id=update.message.from_user.id, text="Write the name for your new character!")
    character = Character.Character(update.message.from_user.username, update.message.text)


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
        replyK.append([KeyboardButton(cmp[:len(cmp)-5])]) # last five characters are ".json"
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the campaign you want to load!",
                             reply_markup=ReplyKeyboardMarkup(replyK, one_time_keyboard=True))
    return ConversationHandler.END


def quitCampaign(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you next time!")
    return ConversationHandler.END

    # TODO: should be a RETURN GAMESTATE or whatever I decide to call the menu when the game starts