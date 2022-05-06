import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from classes import Monster

cwd = os.getcwd()

CHARCREATION, SETNAME, SETEQUIP, FINISHEQUIP = range(4)


def createChar():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.text, setDM)],
        states={
            CHARCREATION: [MessageHandler(Filters.text, charCreation)],
            SETNAME: [MessageHandler(Filters.text, setName)],
            SETEQUIP: [MessageHandler(Filters.text, setEquip)],
            FINISHEQUIP: [MessageHandler(Filters.text, finishSetEquip)]
        },
        fallbacks=[CommandHandler('quit', quit_charCreation)],
        per_user=True,
        per_chat=False
    )


def quit_charCreation(update: Update, context: CallbackContext):
    update.message.reply_text('Okay, bye.')
    return ConversationHandler.END


def setDM(update: Update, context: CallbackContext) -> int:
    path = cwd + "/campaigns"
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    context.user_data["campaignName"] = update.message.text
    open(context.user_data["campaignName"] + ".json", "x")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your campaign has been created successfully! "
                                                                    "The next user that writes a message will be "
                                                                    "the DM.")
    return CHARCREATION


def charCreation(update: Update, context: CallbackContext) -> int:
    dm = {"dm": update.message.from_user.username}
    with open(context.user_data["campaignName"] + ".json", "w") as cmp:
        json.dump(dm, cmp)
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.from_user.username + "is the "
                                                                                                        "Dungeon "
                                                                                                        "Master for "
                                                                                                        "this "
                                                                                                        "campaign.")
    context.bot.send_message(chat_id=update.effective_chat.id, text="Users in the chat that want to play the campaign"
                                                                    "may type the name of their new character here in "
                                                                    "chat. I will start "
                                                                    "a private conversation asking you to create the "
                                                                    "character.")
    return SETNAME


def setName(update: Update, context: CallbackContext):  # starts a private conversation with the user and creates char.
    global character
    character = Character.Character(update.message.from_user.username, update.message.text)
    context.bot.send_message(chat_id=update.message.from_user.id, text="Ok, your character name is " + character.name +
                                                                       "!")
    context.bot.send_message(chat_id=update.message.from_user.id, text="Now choose the race and the class, "
                                                                       "in this order,"
                                                                       "separated by a comma.")
    context.user_data["index"] = 0
    return SETEQUIP


def setEquip(update: Update, context: CallbackContext):
    if context.user_data["index"] == 0:  # if the user just inserted race and class
        text = update.message.text
        text.lower()
        raceClass = text.split(", ")
        character.stats.setStats(raceClass[0], raceClass[1])
        context.user_data["equipList"] = initEquipList(raceClass[1])  # returns the equipment list choice for the class.
    context.user_data["chosenEquip"] = []
    keyboard = []
    if context.user_data["index"] != 0:
        context.user_data["chosenEquip"].append(update.message.text)
    if context.user_data["index"] < len(context.user_data["equipList"]):
        for elem in context.user_data["equipList"][context.user_data["index"]]:
            keyboard.append([KeyboardButton(elem)])
        context.user_data["index"] = context.user_data["index"] + 1
        context.bot.send_message(chat_id=update.message.from_user.id, text="Choose your starting equipment.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return SETEQUIP
    print("Gets here")  # it does indeed get here
    return FINISHEQUIP


def finishSetEquip(update: Update, context: CallbackContext):
    print("Gets here too")
    if context.user_data["index"] == len(context.user_data["equipList"]):
        with open(context.user_data["campaignName"] + ".json", "w") as cmp:
            character.equipment.setInitialEquipment(character.race, character._class, context.user_data["chosenEquip"])
            charInfo = character.json()
            json.dump(charInfo, cmp)
        context.bot.send_message(chat_id=update.message.from_user.id, text="Ok, you're done choosing your equipment!"
                                                                           "Now write 'Done' to save your character.")
    return ConversationHandler.END


def initEquipList(_class: str):
    if _class == "cleric":
        return [["Mace", "Warhammer"], ["Scale Mail", "Leather Armor", "Chain Mail"]]

    if _class == "fighter":
        return [["Chain Mail", "Leather Armor, Longbow"], ["Martial Weapon, Shield", "Martial Weapon, Martial Weapon"],
                ["Light Crossbow", "Handaxe, Handaxe"], ["Dungeoneer's Pack", "Explorer's Pack"]]

    if _class == "rogue":
        return [["Rapier", "Shortbow"], ["Shortbow", "Shortsword"],
                ["Burglar's Pack", "Dungeoneer's Pack", "Explorer's Pack"],
                ["Leather Armor, Dagger, Dagger, Thieves' Tools"]]

    if _class == "wizard":
        return [["Quarterstaff", "Dagger"], ["Component Pouch", "Arcane Focus"], ["Scholar's Pack", "Explorer's Pack"],
                ["Spellbook"]]
