import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from classes import Monster
from classes.JSONEncoder import MyEncoder

cwd = os.getcwd()

CHARCREATION, SETNAME, SETEQUIP, FINISHSPELLS, FINISHCREATION = range(5)


def createChar():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.text, charCreation)],
        states={
            SETNAME: [MessageHandler(Filters.text, setName)],
            SETEQUIP: [MessageHandler(Filters.text & ~Filters.regex(
                "^Scale Mail|Leather Armor|Chain Mail|Dungeoneer's Pack|Explorer's Pack|Leather Armor|Dagger|Thieves' "
                "Tools|Spellbook$ "
            ), setEquip), MessageHandler(Filters.regex(
                "^Dungeoneer's Pack|Explorer's Pack|Leather Armor|Dagger|Thieves' "
                "Tools$ "
            ), finishCreation),
                       MessageHandler(Filters.text, setSpells), MessageHandler(Filters.regex(
                    "^Scale Mail|Leather Armor|Chain Mail|Spellbook$"
                ), setSpells)],
            FINISHSPELLS: [MessageHandler(Filters.text, finishSetSpells)],
            FINISHCREATION: [MessageHandler(Filters.text, finishCreation)]
        },
        fallbacks=[CommandHandler('quit', quit_charCreation)],
        per_user=True,
        per_chat=False
    )


def charCreation(update: Update, context: CallbackContext) -> int:
    # with open(context.user_data["campaignName"] + ".json", "w") as cmp:
    #    json.dump(dm, cmp)
    context.user_data["activeCampaign"] = dict()
    context.user_data["activeCampaign"]["dm"] = update.message.from_user.username
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
    context.bot.send_message(chat_id=update.message.from_user.id, text="Available races: Human, Halfling, Dwarf, Elf")
    context.bot.send_message(chat_id=update.message.from_user.id,
                             text="Available classes: Fighter, Cleric, Wizard, Rogue")
    context.user_data[update.message.from_user.username + "index"] = 0
    return SETEQUIP


def setEquip(update: Update, context: CallbackContext) -> int:
    if context.user_data[update.message.from_user.username + "index"] == 0:  # if the user just inserted race and class
        text = update.message.text
        text.lower()
        raceClass = text.split(", ")
        character.race = raceClass[0]
        character._class = raceClass[1]
        character.stats.setStats(raceClass[0], raceClass[1])
        context.user_data[update.message.from_user.username + "equipList"] = initEquipList(
            raceClass[1])  # returns the equipment list choice for the class.
        context.user_data[update.message.from_user.username + "chosenEquip"] = []
    keyboard = []
    if context.user_data[update.message.from_user.username + "index"] != 0:
        context.user_data[update.message.from_user.username + "chosenEquip"].append(update.message.text)
    if context.user_data["index"] < len(context.user_data["equipList"]):
        for elem in context.user_data[update.message.from_user.username + "equipList"][
            context.user_data[update.message.from_user.username + "index"]]:
            keyboard.append([KeyboardButton(elem)])
        context.user_data[update.message.from_user.username + "index"] = context.user_data[
                                                                             update.message.from_user.username + "index"] + 1
        context.bot.send_message(chat_id=update.message.from_user.id, text="Choose your starting equipment.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return SETEQUIP
    return FINISHCREATION


def setSpells(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Since you chose either to be a wizard"
                                                                    "or a cleric, you have the right to choose"
                                                                    "3 cantrips and 2 level 1 spells. You can write"
                                                                    "the chosen spells here, and they will be added to your inventory.")
    return FINISHSPELLS


def finishSetSpells(update: Update, context: CallbackContext):
    character.setInitialSpells(update.message.text)
    return FINISHCREATION


def finishCreation(update: Update, context: CallbackContext):
    character.equipment.setInitialEquipment(character.race, character._class,
                                            context.user_data[update.message.from_user.username + "chosenEquip"])
    charInfo = json.loads(MyEncoder().encode(character).replace("\"", '"'))
    context.user_data["activeCampaign"][update.message.from_user.username + "char"] = charInfo
    with open(context.user_data["campaignName"] + ".json", "a") as cmp:
        json.dump(context.user_data["activeCampaign"], cmp)
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


def quit_charCreation(update: Update, context: CallbackContext):
    update.message.reply_text('Okay, bye.')
    return ConversationHandler.END
