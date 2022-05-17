import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from classes.JSONEncoder import MyEncoder
from . import charCreationMenu
from classes import Monster

DM, DMCOMBATMENU, PLAYERMENU, RESOLVEITEMCHOICE, MONSTERSPAWNED, CHOOSEITEM, \
CHOOSEHP, RESOLVEHPCHOICE, CHOOSETARGET, DAMAGECALC, ERROR = range(11)

#TODO: MAKE COMBAT END IMMEDIATELY FOR EVERYONE
def activeCamp():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaignDM', menu)],
        states={
            DM: [
                MessageHandler(
                    Filters.text & ~Filters.command('quit') & ~Filters.regex("^Add item to player...|Remove item "
                                                                             "from player...| "
                                                                             "Add spell to player...|Damage player|Heal player|"
                                                                             "Begin combat|Spawn monster|Save campaign$"),
                    dmMenu),
                MessageHandler(Filters.regex("^Add item to "
                                             "player...|Remove item "
                                             "from player...| "
                                             "Add spell to player...|"
                                             "Damage player|Heal player$"),
                               choosePlayer),
                MessageHandler(Filters.regex("^Begin combat$"), dmCombatMenu),
                MessageHandler(Filters.regex("^Spawn monster$"), spawnMonster),
                MessageHandler(Filters.regex("^Save campaign$"), saveCampaign)
            ],
            CHOOSEITEM: [MessageHandler(Filters.text, chooseItem)],
            CHOOSEHP: [MessageHandler(Filters.text, chooseHp)],
            RESOLVEITEMCHOICE: [MessageHandler(Filters.text, resolveItemChoice)],
            RESOLVEHPCHOICE: [MessageHandler(Filters.text, resolveHpChoice)],
            MONSTERSPAWNED: [MessageHandler(Filters.text, monsterSpawned)],
            DMCOMBATMENU: [MessageHandler(Filters.regex("^Begin combat|Done$"), dmCombatMenu),
                           # NEED TO FIND A WAY TO GET BACK HERE FROM DAMAGECALC
                           MessageHandler(Filters.regex("^Make monster attack$"), monsterAttack),
                           MessageHandler(Filters.regex("^End combat$"), dmMenu),
                           MessageHandler(Filters.regex("^Pass$"), monsterAttack)],
            CHOOSETARGET: [MessageHandler(Filters.text, chooseTarget)],
            DAMAGECALC: [MessageHandler(Filters.text, damageCalculation)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)],
        per_user=True,
        per_chat=False  # The DM can write private messages to the bot if he may want to.
    )


def menu(update: Update, context: CallbackContext) -> int:
    if update.message.from_user.username != context.chat_data["activeCampaign"]["dm"]:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're not the DM!")
        return ConversationHandler.END
    context.bot.send_message(chat_id=update.effective_chat.id, text="DM, write anything down to pop up the menu!")
    return DM


def quitCampaign(update: Update, context: CallbackContext):
    saveCampaign(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The campaign has been saved. Goodbye!")
    return ConversationHandler.END


def dmMenu(update: Update, context: CallbackContext) -> int:
    # End combat if the previous state of the game was combat.
    if update.message.text == "End combat":
        context.chat_data.pop("combatOrder")
        context.chat_data.pop("currentPlayer")
        context.chat_data.pop("combatOrderIndex")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Combat has been terminated.")

    menu = [[KeyboardButton("Spawn monster")],
            [KeyboardButton("Begin combat")],
            [KeyboardButton("Add item to player...")],
            [KeyboardButton("Remove item from player...")],
            [KeyboardButton("Add spell to player...")],
            [KeyboardButton("Damage player")],
            [KeyboardButton("Heal player")],
            [KeyboardButton("Save campaign")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                             reply_markup=ReplyKeyboardMarkup(menu,
                                                              one_time_keyboard=True,
                                                              selective=True),
                             reply_to_message_id=update.message.message_id)
    return DM


# Dm utility functions.
def saveCampaign(update: Update, context: CallbackContext):
    data = dict()
    data["dm"] = context.chat_data["activeCampaign"]["dm"]
    print(context.chat_data["activeCampaign"])
    for key in context.chat_data["activeCampaign"]:
        if key.endswith("char"):
            charInfo = json.loads(MyEncoder().encode(context.chat_data["activeCampaign"][key]).replace("\"", '"'))
            charData = dict()
            charData[key] = charInfo
            data.update(charData)
        elif key.endswith("monster"):
            monsterInfo = json.loads(MyEncoder().encode(context.chat_data["activeCampaign"][key]).replace("\"", '"'))
            monsterData = dict()
            monsterData[key] = monsterInfo
            data.update(monsterData)
    with open(context.bot_data["campaignName"] + ".json", "w") as cmp:
        json.dump(data, cmp, indent=4)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The campaign has been saved. Type anything "
                                                                    "to resume the game.")
    return DM


def spawnMonster(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write down the name of the monster that you "
                                                                    "want to spawn.")
    return MONSTERSPAWNED


def monsterSpawned(update: Update, context: CallbackContext):
    monsterName = update.message.text
    monster = Monster.Monster(monsterName)  # regardless of anything the monster name will be in uppercase
    context.chat_data["activeCampaign"][monster.name + "monster"] = monster
    context.bot.send_message(chat_id=update.effective_chat.id, text=monster.name + " has been spawned.")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=context.chat_data["activeCampaign"][
                                      monster.name + "monster"].name + " statblock:")  # TODO: insert statblock
    return DM


def choosePlayer(update: Update, context: CallbackContext):
    players = []
    for key in context.chat_data["activeCampaign"]:
        if key.endswith("char"):
            players.append([KeyboardButton(context.chat_data["activeCampaign"][key].name)])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.",
                             reply_markup=ReplyKeyboardMarkup(players))
    context.chat_data["dmChoice"] = update.message.text
    if update.message.text == "Add item to player..." or update.message.text == "Remove item from player..." or update.message.text == "Add spell to player...":
        return CHOOSEITEM
    return CHOOSEHP


def chooseItem(update: Update, context: CallbackContext):
    context.chat_data["chosenPlayer"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the item/spell to add/remove.")
    return RESOLVEITEMCHOICE


def resolveItemChoice(update: Update, context: CallbackContext):
    error = ""
    if context.chat_data["dmChoice"] == "Add item to player...":
        chosenPlayer = context.chat_data["chosenPlayer"]
        item = update.message.text
        error = context.chat_data["activeCampaign"][chosenPlayer + "char"].addItem(item)
    elif context.chat_data["dmChoice"] == "Remove item to player...":
        chosenPlayer = context.chat_data["chosenPlayer"]
        item = update.message.text
        error = context.chat_data["activeCampaign"][chosenPlayer + "char"].rmItem(item)
    elif context.chat_data["dmChoice"] == "Add spell to player...":
        chosenPlayer = context.chat_data["chosenPlayer"]
        spell = update.message.text
        error = context.chat_data["activeCampaign"][chosenPlayer + "char"].addSpell(spell)

    context.bot.send_message(chat_id=update.effective_chat.id, text="The action was successful." + str(error))
    return DM


def chooseHp(update: Update, context: CallbackContext):
    context.chat_data["chosenPlayer"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write the amount of health to alter.")
    return RESOLVEHPCHOICE


def resolveHpChoice(update: Update, context: CallbackContext):
    oldHp = context.chat_data["activeCampaign"][context.chat_data["chosenPlayer"] + "char"].stats.hp
    context.chat_data["activeCampaign"][context.chat_data["chosenPlayer"] + "char"].stats.hp += int(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Health changed. Old hp: " + str(oldHp) + " ,"
                                                                                                              "new hp: " +
                                                                    str(context.chat_data["activeCampaign"][
                                                                            context.chat_data[
                                                                                "chosenPlayer"] + "char"].stats.hp))
    return DM


# DM combat functions.

# FUNCTION NEVER CALLED IN THE CONVERSATIONHANDLER, USED FOR BEGIN COMBAT COMMAND
def influence(update: Update, context: CallbackContext):
    combatOrder = []
    # This for loop checks for all the occurrences of players and monsters in the context.chat_data dict,
    # and makes them all roll for initiative.
    for key in context.chat_data["activeCampaign"]:  # int((self.dex - 10) / 2)
        if key.endswith("char"):
            initiative = context.chat_data["activeCampaign"][key].roll("d20", context.chat_data["activeCampaign"][
                key].stats.dexMod)
            combatOrder.append((context.chat_data["activeCampaign"][key].name, initiative, key))
            context.bot.send_message(chat_id=update.effective_chat.id, text=
            context.chat_data["activeCampaign"][key].name + " rolled " + str(initiative))
        if key.endswith("monster"):
            initiative = context.chat_data["activeCampaign"][key].roll("d20", (
                        context.chat_data["activeCampaign"][key].dex - 10) / 2)
            combatOrder.append((context.chat_data["activeCampaign"][key].name, initiative, key))
            context.bot.send_message(chat_id=update.effective_chat.id, text=
            context.chat_data["activeCampaign"][key].name + " rolled " + str(initiative))

    # sort the list by initiative to get the order of combat; THIS DOES NOTHING
    combatOrder = sorted(combatOrder, key=lambda x: x[1], reverse=True)
    context.chat_data["combatOrder"] = combatOrder

    # first element of the tuple of the first element of the list
    context.chat_data["currentPlayer"] = combatOrder[0][0]

    # declaring a combat order index to go through all the entities involved in combat, like using a for loop
    context.chat_data["combatOrderIndex"] = 0

    # helps with determining whose turn it is, it's the name of the entity as it appears on the json
    context.chat_data["currentPlayerKey"] = combatOrder[0][2]

    # sending a message to inform everyone about the combat order.
    order = []
    for i in range(len(combatOrder)):
        order.append(combatOrder[i][0])
    order = ", ".join(order)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Combat order: " + order)

    # Telling whose turn it is the first time around.
    context.bot.send_message(chat_id=update.effective_chat.id, text="It's " + context.chat_data["currentPlayer"] +
                                                                    "'s turn!")
    return DMCOMBATMENU


def dmCombatMenu(update: Update, context: CallbackContext):
    if "combatOrder" not in context.chat_data:
        influence(update, context)
    else:  # TODO: NEEDS TO BE REWORKED

        context.bot.send_message(chat_id=update.effective_chat.id, text="It's " + context.chat_data["currentPlayer"] +
                                                                        "'s turn!")

    keyboard = [[KeyboardButton("Make monster attack")], [KeyboardButton("Pass")], [KeyboardButton("End combat")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an action to perform in combat.",
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return DMCOMBATMENU


def monsterAttack(update: Update, context: CallbackContext):
    # the DM just needs to check if the current player isn't a player.
    # if it's not a player, then he gets a list of actions the monster can perform.
    keyboard = []
    if context.chat_data["currentPlayerKey"].endswith("monster"):
        if update.message.text == "Pass":
            context.chat_data["combatOrderIndex"] = context.chat_data["combatOrderIndex"] + 1
            if context.chat_data["combatOrderIndex"] == len(context.chat_data["combatOrder"]):
                context.chat_data["combatOrderIndex"] = 0
            context.chat_data["currentPlayer"] = \
                context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][0]
            context.chat_data["currentPlayerKey"] = \
            context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][2]
            context.bot.send_message(chat_id=update.effective_chat.id, text="The DM has chosen to pass the turn. He "
                                                                            "may type anything to let other players"
                                                                            "play.")
            return DMCOMBATMENU
        monster = context.chat_data["activeCampaign"][context.chat_data["currentPlayer"] + "monster"]
        for action in monster.actions:
            keyboard.append([KeyboardButton(action["name"] + ": " + action["desc"])])
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choose from this list of actions.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=True),
                                 reply_to_message_id=update.message.message_id)
        return CHOOSETARGET
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="It's not your turn yet!")


def chooseTarget(update: Update, context: CallbackContext):
    context.chat_data["dmChoice"] = update.message.text
    players = []
    for key in context.chat_data:
        if key.endswith("char"):
            players.append(context.chat_data["activeCampaign"][key]["name"])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.",
                             reply_markup=ReplyKeyboardMarkup(players, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return DAMAGECALC


def damageCalculation(update: Update, context: CallbackContext):
    targetPlayer = update.message.text
    # this is because the former is a description, that ends with that symbol.
    monsterAction = context.chat_data["dmChoice"]
    monsterAction = monsterAction.partition(':')[0]
    monster = context.chat_data["activeCampaign"][context.chat_data["currentPlayer"] + "monster"]
    damage = monster.attack(monsterAction)
    msg = context.chat_data["activeCampaign"][targetPlayer + "char"].stats.takeDamage(damage)
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    if context.chat_data["activeCampaign"][targetPlayer + "char"].stats.hp <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Oh no! The player died!")
        # del context.chat_data["activeCampaign"][targetPlayer + "char"] ? I don't know if I want to delete che char right away

    # The turn changes to the next player in the combat order list.
    context.chat_data["combatOrderIndex"] = context.chat_data["combatOrderIndex"] + 1
    if context.chat_data["combatOrderIndex"] == len(context.chat_data["combatOrder"]):
        context.chat_data["combatOrderIndex"] = 0
    context.chat_data["currentPlayer"] = context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][0]
    context.chat_data["currentPlayerKey"] = context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][2]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Write 'Done' to move on to the next entity's turn.")
    return DMCOMBATMENU
