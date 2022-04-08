import random
from telegram import *
from telegram.ext import *
import os
import json
from classes import Character

menuRollback = "^d4|d8|d12|d20$"  # Complete with all the messages that make you go back to the menu

cwd = os.getcwd() + "/campaigns"
os.chdir(cwd)
campaignList = os.listdir()
campaignListRegex = "^"
for camp in campaignList:
    campaignListRegex = campaignListRegex + camp + "|"
campaignListRegex = campaignListRegex + "$"

MENU, ROLL, COMBAT, QUIT, MOVE, ACTION, ACTIONS = range(6)


def start_cmd():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(campaignListRegex), loadCharacter)],
        states={
            MENU: [MessageHandler(Filters.regex(menuRollback), menu), MessageHandler(Filters.regex("^roll$"), roll)],
            ROLL: [MessageHandler(Filters.regex("^d4|d8|d12|d20$"), die)],
            COMBAT: combat_hnd()
        },
        fallbacks=[MessageHandler(Filters.regex("^Quit$"), quitCamp)]
    )


def loadCharacter(update: Update, context: CallbackContext) -> int:
    global chosenCmp
    chosenCmp = str(update.message.text) + ".json"
    loadedCamp = open(chosenCmp + ".json", "r")
    global camp
    camp = json.load(loadedCamp)
    loadedCamp.close()
    pid = str(update.message.from_user)
    global character
    character = Character.Character(camp[pid]["race"], camp[pid]["class"], camp[pid]["statistics"],
                                    camp[pid]["description"], camp[pid]["equipment"])
    return MENU  #this doesn't work: the user needs to type something in order to proceed with the game


def menu(update: Update, context: CallbackContext) -> int:
    actions = [KeyboardButton("Roll"), KeyboardButton("Combat"), KeyboardButton("Print attributes"),
               KeyboardButton("Quit")]
    context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=actions)
    return MENU


###########################ROLL A DICE##############################

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


#############################COMBAT STUFF#############################

def combat_hnd():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("^Combat$"), combat)],
        states={
            COMBAT: [MessageHandler(Filters.regex("^Move$"), move), MessageHandler(Filters.regex("^Action$"), action)],
            MOVE: [MessageHandler(Filters.regex("/D"), move)],
            ACTION: action_cmh()
        },
        fallbacks=[MessageHandler(Filters.regex("^Quit combat$"), menu)],
        map_to_parent={

        }
    )


def combat(update: Update, context: CallbackContext) -> int:
    # Tough: got to make sure that the player can only
    # do them twice, or more if made possible by modifiers
    combatOptions = [KeyboardButton("Move"), KeyboardButton("Action"), KeyboardButton("End turn")]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the action you want to take.",
                             reply_markup=combatOptions)
    return COMBAT


def move(update: Update, context: CallbackContext) -> int:
    cells = character.getStats().getSpeed()
    context.bot.send_message(chat_id=update.effective_chat.id, text="How many cells would you want to move?")
    ans = int(update.message.text)
    if ans > cells:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You can't move for more than your speed allows"
                                                                        "you!")
        return MOVE
    cells = cells - ans
    if cells != 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Would you like to take action or move again?")
    if cells == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You can't move any further!")
    return COMBAT


def action_cmh():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("^Action$"), action)],
        states={
            ACTIONS: [MessageHandler(Filters.regex("^Attack$"), attack)]
        },
        fallbacks=[]
    )


def action(update: Update, context: CallbackContext) -> int:
    actions = [KeyboardButton("Attack"), KeyboardButton("Cast a spell"), KeyboardButton("Dash"), KeyboardButton("Disengage"),
               KeyboardButton("Dodge"), KeyboardButton("Help"), KeyboardButton("Hide"), KeyboardButton("Ready"),
               KeyboardButton("Search"), KeyboardButton("Use object")]
    context.bot.send_message(chat_id=update.effective_chat.id, text="What action would you like to take?",
                             reply_markup= actions)
    return ACTIONS


def attack(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose a target for the attack")


############################QUIT CAMPAIGN####################################

def quitCamp(update: Update, context: CallbackContext):
    loadedCamp = open(chosenCmp + ".json", "w")
    json.dump(camp, loadedCamp)  # save the modified camp to loadedCamp
    loadedCamp.close()
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your campaign has been saved successfully.")

