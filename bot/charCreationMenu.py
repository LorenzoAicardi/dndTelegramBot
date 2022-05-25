import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from classes import Monster
from classes import Equipment
from classes.JSONEncoder import MyEncoder

cwd = os.getcwd()

CHARCREATION, SETNAME, SETEQUIP, FINISHSPELLS, FINISHCREATION, SETSPELLS = map(chr, range(6))


def createChar():
    return ConversationHandler(
        entry_points=[CommandHandler('createChar', charCreation)],
        states={
            SETNAME: [MessageHandler(Filters.text, setName)],
            SETEQUIP: [MessageHandler(Filters.text & ~Filters.regex("^Done|done$") & ~Filters.regex("^Spells|spells$"), setEquip),
                       MessageHandler(Filters.regex("^Done|done$"), finishCreation),
                       MessageHandler(Filters.regex("^Spells|spells$"), setSpells)],
            FINISHCREATION: [MessageHandler(Filters.text, finishCreation)]
        },
        fallbacks=[CommandHandler('quit', quit_charCreation)],
        per_user=True,
        per_chat=False
    )


def charCreation(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.message.from_user.id, text="Welcome to the character creation menu! "
                                                                       "Write your character name. You can quit "
                                                                       "character creation at any time by "
                                                                       "typing command /quit.")
    return SETNAME


def setName(update: Update, context: CallbackContext):  # starts a private conversation with the user and creates char.
    global character
    character = Character.Character(update.message.from_user.username, update.message.text)
    context.bot.send_message(chat_id=update.message.from_user.id, text="Ok, your character name is " + character.name +
                                                                       "!")
    context.bot.send_message(chat_id=update.message.from_user.id, text="Now choose the race and the class, "
                                                                       "in this order,"
                                                                       "separated by a comma.")
    context.bot.send_message(chat_id=update.message.from_user.id, text="Available races: Human, Halfling, Dwarf, Elf")
    context.bot.send_message(chat_id=update.message.from_user.id,
                             text="Available classes: Fighter, Cleric, Wizard, Rogue")
    context.user_data[update.message.from_user.username + "firstTime"] = True
    return SETEQUIP


def setEquip(update: Update,
             context: CallbackContext) -> int:

    if context.user_data[update.message.from_user.username + "firstTime"]:
        # if the user just inserted race and class
        text = update.message.text
        text = text.lower()
        raceClass = text.split(", ")
        raceClass[0] = raceClass[0].strip()
        raceClass[1] = raceClass[1].strip()
        character.race = raceClass[0]  # character race
        character._class = raceClass[1]  # character class
        character.stats.setStats(raceClass[0], raceClass[1])
        context.user_data[update.message.from_user.username + "equipList"] = initEquipList(
            raceClass[1])  # returns the equipment list choice for the class.
        context.user_data[update.message.from_user.username + "chosenEquip"] = []
        context.user_data[update.message.from_user.username + "index"] = 0
        context.user_data[update.message.from_user.username + "firstTime"] = False

    keyboard = []
    if context.user_data[update.message.from_user.username + "index"] != 0:
        context.user_data[update.message.from_user.username + "chosenEquip"].append(update.message.text)
    if context.user_data[update.message.from_user.username + "index"] < len(
            context.user_data[update.message.from_user.username + "equipList"]):
        for elem in \
                context.user_data[update.message.from_user.username + "equipList"][
                    context.user_data[update.message.from_user.username + "index"]]:
            keyboard.append([KeyboardButton(elem)])
        context.bot.send_message(chat_id=update.message.from_user.id, text="Choose your starting equipment.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        context.user_data[update.message.from_user.username + "index"] = context.user_data[
                                                                             update.message.from_user.username + "index"] + 1
        # the else is for when I AM DONE ITERATING
    else:
        context.bot.send_message(chat_id=update.message.from_user.id, text="Ok, write 'Done' to save your character. "
                                                                           "If you chose to be either a wizard or"
                                                                           " a cleric, please write 'Spells' to set "
                                                                           "your spells.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

    return SETEQUIP


def setSpells(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="You have the right to choose "
                                                                    "3 cantrips and 2 level 1 spells. You can write "
                                                                    "the chosen spells here, "
                                                                    "and they will be added to your inventory.")
    return FINISHCREATION


def finishCreation(update: Update, context: CallbackContext):
    if character._class == "cleric" or character._class == "wizard":
        character.setInitialSpells(update.message.text)

    context.user_data["activeCampaign"] = dict()
    noItem = character.equipment.setInitialEquipment(character.race, character._class,
                                                     context.user_data[
                                                         update.message.from_user.username + "chosenEquip"])
    if noItem != "":
        context.bot.send_message(chat_id=update.effective_chat.id, text=noItem)
    context.user_data["activeCampaign"][update.message.from_user.username + "char"] = character
    charInfo = json.loads(MyEncoder().encode(character).replace("\"", '"'))
    context.user_data["charToSave"] = dict()
    context.user_data["charToSave"][update.message.from_user.username + "char"] = charInfo
    with open(context.bot_data["campaignName"] + ".json", "r+") as file:
        # TODO: CHECK IF IT WORKS WHEN ADDING MULTIPLE CHARACTERS
        totalCamp = json.load(file)
        file.truncate(0)
        totalCamp.update(context.user_data["charToSave"])
        json.dump(totalCamp, file, indent=4)
    context.bot.send_message(chat_id=update.message.from_user.id, text="Ok, you're done choosing your equipment!")
    context.bot.send_message(chat_id=context.bot_data["Group chat id"], text=update.message.from_user.username +
                                                                             " is done creating their character, "
                                                                             "and may type command /startCampaign "
                                                                             "to open his menu.")
    return ConversationHandler.END


def initEquipList(_class: str):
    _class = _class.lower()
    if _class == "cleric":
        return [["Mace", "Warhammer"], ["Scale Mail", "Leather Armor", "Chain Mail"]]

    if _class == "fighter":
        return [["Chain Mail", "Leather Armor, Longbow"], ["Martial Weapon, Shield", "Martial Weapon, Martial Weapon"],
                ["Crossbow, Light", "Handaxe, Handaxe"], ["Dungeoneer's Pack", "Explorer's Pack"]]

    if _class == "rogue":
        return [["Rapier", "Shortbow"], ["Shortbow", "Shortsword"],
                ["Burglar's Pack", "Dungeoneer's Pack", "Explorer's Pack"],
                ["Leather Armor, Dagger, Dagger, Thieves' Tools"]]

    if _class == "wizard":
        return [["Quarterstaff", "Dagger"], ["Component Pouch", "Arcane Focus"], ["Scholar's Pack", "Explorer's Pack"],
                ["Spellbook"]]


def quit_charCreation(update: Update, context: CallbackContext):
    update.message.reply_text('Okay, bye.')
    return ConversationHandler.END
