import json
from telegram import *
from telegram.ext import *
import os
from classes import Character
from . import initialMenu
from classes import Monster

DM, DMMENU, DMCOMBATMENU, PLAYERMENU = range(4)


def activeCamp():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaign', menu)],
        states={
            PLAYERMENU: [MessageHandler(Filters.text, playerMenu)],  # add playermenu
            DM: [MessageHandler(Filters.text, dmMenu), MessageHandler(Filters.regex("^Add item to "
                                                                                               "player...|Remove item "
                                                                                               "from player...| "
                                              "Add spell to player...|Damage player|Heal player$"), choosePlayer),
                 MessageHandler(Filters.regex("^Add item to player...|"
                                              "Remove item from player...|Add spell to player...$"), chooseItem),
                 MessageHandler(Filters.text, choice),
                 MessageHandler(Filters.regex("^Begin combat$"), influence),
                 MessageHandler(Filters.regex("^Spawn monster$"), spawnMonster),
                 MessageHandler(Filters.text, monsterSpawned)],  # TODO: PUT A BETTER FILTER
            DMCOMBATMENU: [MessageHandler(Filters.regex("^Begin combat$"), dmCombatMenu),
                           MessageHandler(Filters.regex("^Make monster attack$"), monsterAttack),
                           MessageHandler(Filters.text, chooseTarget),  # TODO: NEED TO PUT BETTER FILTERS
                           MessageHandler(Filters.text, damageCalculation),
                           MessageHandler(Filters.text, dmCombatMenu)]
        },
        fallbacks=[],
        per_user=False,
        per_chat=True
    )


def menu(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write anything down to pop up the menu!")
    if update.message.from_user.username == context.user_data["activeCampaign"]["dm"]:
        return DM
    return PLAYERMENU


def playerMenu(update: Update, context: CallbackContext):
    menu = [[KeyboardButton("Attack")],
            [KeyboardButton("Roll")],
            [KeyboardButton("Rest")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                             reply_markup=ReplyKeyboardMarkup(menu, one_time_keyboard=True))
    return PLAYERMENU


def dmMenu(update: Update, context: CallbackContext) -> int:
    menu = [[KeyboardButton("Spawn monster")],
            [KeyboardButton("Begin combat")],
            [KeyboardButton("Add item to player...")],
            [KeyboardButton("Remove item from player...")],
            [KeyboardButton("Add spell to player...")],
            [KeyboardButton("Damage player")],
            [KeyboardButton("Heal player")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                             reply_markup=ReplyKeyboardMarkup(menu, one_time_keyboard=True))
    return DM


def spawnMonster(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write down the name of the monster that you"
                                                                    "want to spawn.")
    return DM


def monsterSpawned(update: Update, context: CallbackContext):
    monsterName = update.message.text
    monster = Monster.Monster(monsterName)
    context.user_data["activeCampaign"][monster.name + "monster"] = monster
    context.bot.send_message(chat_id=update.effective_chat.id, text=monster.name + " has been spawned.")
    return DMMENU


def choosePlayer(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.")
    context.user_data["dmChoice"] = update.message.text
    return DM


def chooseItem(update: Update, context: CallbackContext):
    context.user_data["chosenPlayer"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the item/spell to add/remove.")
    return DM


def choice(update: Update, context: CallbackContext):
    if context.user_data["dmChoice"] == "Add item to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        item = update.message.text
        context.user_data[chosenPlayer + "char"].addItem(item)
        return DMMENU
    elif context.user_data["dmChoice"] == "Remove item to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        item = update.message.text
        context.user_data[chosenPlayer + "char"].rmItem(item)
        return DMMENU
    elif context.user_data["dmChoice"] == "Add spell to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        spell = update.message.text
        context.user_data[chosenPlayer + "char"].addSpell(spell)
        return DMMENU


def influence(update: Update, context: CallbackContext):
    combatOrder = []
    # This for loop checks for all the occurrences of players and monsters in the context.user_data dict,
    # and makes them all roll for initiative.
    for key in context.user_data:  # int((self.dex - 10) / 2)
        if key.endswith("char"):
            initiative = context.user_data[key].roll("d20", context.user_data[key]["stats"]["dexMod"])
            combatOrder.append((context.user_data[key]["name"], initiative))
        if key.endswith("monster"):
            initiative = context.user_data[key].roll("d20", (context.user_data[key]["stats"]["dex"] - 10) / 2)
            combatOrder.append((context.user_data[key]["name"], initiative))

    # sort the list by initiative to get the order of combat
    context.user_data["combatOrder"] = sorted(combatOrder, key=lambda x: x[1], reverse=True)

    # first element of the tuple of the first element of the list
    context.user_data["currentPlayer"] = combatOrder[0][0]

    # declaring a combat order index to go through all the entities involved in combat
    context.user_data["combatOrderIndex"] = 0

    context.bot.send_message(chat_id=update.effective_chat.id, text="It's " + context.user_data["currentPlayer"] +
                                                                    "'s turn!")
    return DMCOMBATMENU


def dmCombatMenu(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("Make monster attack")], [KeyboardButton("Pass")]]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return DMCOMBATMENU


def monsterAttack(update: Update, context: CallbackContext):
    # the DM just needs to check if the current player isn't a monster.
    # if it's not a monster, then he gets a list of actions the monster can perform.
    keyboard = []
    if not context.user_data["currentPlayer"].endswith("char"):
        monster = context.user_data[context.user_data["currentPlayer"] + "monster"]
        for action in monster.actions:
            keyboard.append((action["name"], action["description"]))
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choose from this list of actions.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return DMCOMBATMENU


def chooseTarget(update: Update, context: CallbackContext):
    context.user_data["dmChoice"] = update.message.text
    players = []
    for key in context.user_data:
        if key.endswith("char"):
            players.append(context.user_data[key]["name"])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.",
                             reply_markup=ReplyKeyboardMarkup(players))
    return DMCOMBATMENU


def damageCalculation(update: Update, context: CallbackContext):
    targetPlayer = update.message.text
    monsterAction = context.user_data["dmChoice"]
    monster = context.user_data[context.user_data["currentPlayer"] + "monster"]
    damage = monster.attack(monsterAction)
    msg = context.user_data[context.user_data[targetPlayer] + "char"].takeDamage(damage)
    if msg is None:
        # returns the message that determines whether the attack missed or player has died
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The attack hit successfully!")
        hp = context.user_data[context.user_data[targetPlayer] + "char"].stats.hp
        context.bot.send_message(chat_id=update.effective_chat.id, text="Player remaining health: " + hp + "hp.")
    # The turn changes to the next player in the combat order list.
    context.user_data["combatOrderIndex"] = context.user_data["combatOrderIndex"] + 1
    context.user_data["currentPlayer"] = context.user_data["combatOrder"][context.user_data["combatOrderIndex"]][0]
    return DMCOMBATMENU
