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


def activeCamp():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaignDM', menu)],
        states={
            ERROR: [MessageHandler(Filters.text, playerMenu)],

            PLAYERMENU: [MessageHandler(Filters.text, playerMenu)],  # add playermenu

            DM: [
                MessageHandler(
                    Filters.text & ~Filters.command('quit') & ~Filters.regex("^Add item to player...|Remove item "
                                                                             "from player...| "
                                                                             "Add spell to player...|Damage player|Heal player|"
                                                                             "Begin combat|Spawn monster|Save campaign$"),
                    dmMenu),
                MessageHandler(Filters.regex("^Add item to "  # TODO: COULD BE BETTER...
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
            DMCOMBATMENU: [MessageHandler(Filters.regex("^Begin combat|Done$"), dmCombatMenu),  # NEED TO FIND A WAY TO GET BACK HERE FROM DAMAGECALC
                           MessageHandler(Filters.regex("^Make monster attack$"), monsterAttack),
                           MessageHandler(Filters.regex("^End combat$"), dmMenu),
                           MessageHandler(Filters.regex("^Pass$"), monsterAttack)],
            CHOOSETARGET: [MessageHandler(Filters.text, chooseTarget)],
            DAMAGECALC: [MessageHandler(Filters.text, damageCalculation)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)],
        per_user=False,
        per_chat=True
    )


# TODO: Add player menus.


def menu(update: Update, context: CallbackContext) -> int:
    if update.message.from_user.username != context.user_data["activeCampaign"]["dm"]:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're not the DM!")
        return ConversationHandler.END
    context.bot.send_message(chat_id=update.effective_chat.id, text="DM, write anything down to pop up the menu!")
    return DM


def quitCampaign(update: Update, context: CallbackContext):
    saveCampaign(update, context)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The campaign has been saved. Goodbye!")
    return ConversationHandler.END


### PLAYER STUFF ###


def playerMenu(update: Update, context: CallbackContext):
    menu = [[KeyboardButton("Attack")],
            [KeyboardButton("Roll")],
            [KeyboardButton("Rest")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                             reply_markup=ReplyKeyboardMarkup(menu, one_time_keyboard=True))
    return PLAYERMENU






### DM STUFF ###


def dmMenu(update: Update, context: CallbackContext) -> int:
    if update.message.text == "End combat":
        context.user_data.pop("combatOrder")
        context.user_data.pop("currentPlayer")
        context.user_data.pop("combatOrderIndex")
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
                                                              one_time_keyboard=True))
    return DM


#Dm utility functions.
def saveCampaign(update: Update, context: CallbackContext):
    data = dict()
    data["dm"] = context.user_data["activeCampaign"]["dm"]
    for key in context.user_data["activeCampaign"]:
        if key.endswith("char"):
            charInfo = json.loads(MyEncoder().encode(context.user_data["activeCampaign"][key]).replace("\"", '"'))
            charData = dict()
            charData[key] = charInfo
            data.update(charData)
        elif key.endswith("monster"):
            monsterInfo = json.loads(MyEncoder().encode(context.user_data["activeCampaign"][key]).replace("\"", '"'))
            monsterData = dict()
            monsterData[key] = monsterInfo
            data.update(monsterData)
    with open(context.user_data["campaignName"] + ".json", "w") as cmp:
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
    monster = Monster.Monster(monsterName)
    context.user_data["activeCampaign"][monster.name + "monster"] = monster
    context.bot.send_message(chat_id=update.effective_chat.id, text=monster.name + " has been spawned.")
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=context.user_data["activeCampaign"][
                                      monster.name + "monster"].name + " statblock:")  # TODO: insert statblock
    return DM


def choosePlayer(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.")
    context.user_data["dmChoice"] = update.message.text
    if update.message.text == "Add item to player..." or update.message.text == "Remove item from player..." or update.message.text == "Add spell to player...":
        return CHOOSEITEM
    return CHOOSEHP


def chooseItem(update: Update, context: CallbackContext):
    context.user_data["chosenPlayer"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the item/spell to add/remove.")
    return RESOLVEITEMCHOICE


def resolveItemChoice(update: Update, context: CallbackContext):
    error = ""
    if context.user_data["dmChoice"] == "Add item to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        item = update.message.text
        error = context.user_data["activeCampaign"][chosenPlayer + "char"].addItem(item)
    elif context.user_data["dmChoice"] == "Remove item to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        item = update.message.text
        error = context.user_data["activeCampaign"][chosenPlayer + "char"].rmItem(item)
    elif context.user_data["dmChoice"] == "Add spell to player...":
        chosenPlayer = context.user_data["chosenPlayer"]
        spell = update.message.text
        error = context.user_data["activeCampaign"][chosenPlayer + "char"].addSpell(spell)

    if error != "":
        context.bot.send_message(chat_id=update.effective_chat.id, text=error)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The action was successful.")
    return DM


def chooseHp(update: Update, context: CallbackContext):
    context.user_data["chosenPlayer"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write the amount of health to alter.")
    return RESOLVEHPCHOICE


def resolveHpChoice(update: Update, context: CallbackContext):
    oldHp = context.user_data["activeCampaign"][context.user_data["chosenPlayer"] + "char"].stats.hp
    context.user_data["activeCampaign"][context.user_data["chosenPlayer"] + "char"].stats.hp += int(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Health changed. Old hp: " + str(oldHp) + " ,"
                                                                    "new hp: " +
                             str(context.user_data["activeCampaign"][context.user_data["chosenPlayer"] + "char"].stats.hp))
    return DM


#DM combat functions.

# FUNCTION NEVER CALLED IN THE CONVERSATIONHANDLER, USED FOR BEGIN COMBAT COMMAND
def influence(update: Update, context: CallbackContext):
    combatOrder = []
    # This for loop checks for all the occurrences of players and monsters in the context.user_data dict,
    # and makes them all roll for initiative.
    for key in context.user_data["activeCampaign"]:  # int((self.dex - 10) / 2)
        if key.endswith("char"):
            initiative = context.user_data["activeCampaign"][key].roll("d20", context.user_data["activeCampaign"][key].stats.dexMod)
            combatOrder.append((context.user_data["activeCampaign"][key].name, initiative, key))
            context.bot.send_message(chat_id=update.effective_chat.id, text=
                                    context.user_data["activeCampaign"][key].name + " rolled " + str(initiative))
        if key.endswith("monster"):
            initiative = context.user_data["activeCampaign"][key].roll("d20", (context.user_data["activeCampaign"][key].dex - 10) / 2)
            combatOrder.append((context.user_data["activeCampaign"][key].name, initiative, key))
            context.bot.send_message(chat_id=update.effective_chat.id, text=
                                    context.user_data["activeCampaign"][key].name + " rolled " + str(initiative))

    # sort the list by initiative to get the order of combat; THIS DOES NOTHING
    combatOrder = sorted(combatOrder, key=lambda x: x[1], reverse=True)
    context.user_data["combatOrder"] = combatOrder

    # first element of the tuple of the first element of the list
    context.user_data["currentPlayer"] = combatOrder[0][0]

    # declaring a combat order index to go through all the entities involved in combat
    context.user_data["combatOrderIndex"] = 0

    # helps with determining whose turn it is.
    context.user_data["currentPlayerKey"] = combatOrder[0][2]

    # sending a message to inform everyone about the combat order.
    order = []
    for i in range(len(combatOrder)):
        order.append(combatOrder[i][0])
    order = ", ".join(order)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Combat order: " + order)

    # Telling whose turn it is the first time around.
    context.bot.send_message(chat_id=update.effective_chat.id, text="It's " + context.user_data["currentPlayer"] +
                                                                    "'s turn!")
    return DMCOMBATMENU


def dmCombatMenu(update: Update, context: CallbackContext):
    if "combatOrder" not in context.user_data:
        influence(update, context)
    else:  # TODO: NEEDS TO BE REWORKED
        context.bot.send_message(chat_id=update.effective_chat.id, text="It's " + context.user_data["currentPlayer"] +
                                                                        "'s turn!")

    keyboard = [[KeyboardButton("Make monster attack")], [KeyboardButton("Pass")], [KeyboardButton("End combat")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an action to perform in combat.",
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return DMCOMBATMENU


def monsterAttack(update: Update, context: CallbackContext):
    # the DM just needs to check if the current player isn't a player.
    # if it's not a player, then he gets a list of actions the monster can perform.
    keyboard = []
    if context.user_data["currentPlayerKey"].endswith("monster"):
        if update.message.text == "Pass":
            context.user_data["combatOrderIndex"] = context.user_data["combatOrderIndex"] + 1
            context.user_data["currentPlayer"] = \
                context.user_data["combatOrder"][context.user_data["combatOrderIndex"]][0]
            context.user_data["currentPlayerKey"] = context.user_data["combatOrder"][context.user_data["combatOrderIndex"]][2]
            context.bot.send_message(chat_id=update.effective_chat.id, text="The DM has chosen to pass the turn. He"
                                                                            "may type 'Done' to let other players"
                                                                            "play.")
            return DMCOMBATMENU
        monster = context.user_data["activeCampaign"][context.user_data["currentPlayer"] + "monster"]
        for action in monster.actions:
            keyboard.append([KeyboardButton(action["name"] + ": " + action["desc"])])
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choose from this list of actions.",
                                 reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return CHOOSETARGET
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="It's not your turn yet!")


def chooseTarget(update: Update, context: CallbackContext):
    context.user_data["dmChoice"] = update.message.text
    players = []
    for key in context.user_data:
        if key.endswith("char"):
            players.append(context.user_data["activeCampaign"][key]["name"])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the target player.",
                             reply_markup=ReplyKeyboardMarkup(players))
    return DAMAGECALC


def damageCalculation(update: Update, context: CallbackContext):
    targetPlayer = update.message.text
    monsterAction = context.user_data["dmChoice"]
    monsterAction = monsterAction.partition(':')[0]
    monster = context.user_data["activeCampaign"][context.user_data["currentPlayer"] + "monster"]
    damage = monster.attack(monsterAction)
    print(damage)
    msg = context.user_data["activeCampaign"][targetPlayer + "char"].stats.takeDamage(damage)
    if msg is not None:
        # returns the message that determines whether the attack missed or player has died
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The attack hit successfully!")
        hp = context.user_data["activeCampaign"][targetPlayer + "char"].stats.hp
        context.bot.send_message(chat_id=update.effective_chat.id, text="Player remaining health: " + str(hp) + "hp.")

    # The turn changes to the next player in the combat order list.
    context.user_data["combatOrderIndex"] = context.user_data["combatOrderIndex"] + 1
    context.user_data["currentPlayer"] = context.user_data["combatOrder"][context.user_data["combatOrderIndex"]][0]
    context.user_data["currentPlayerKey"] = context.user_data["combatOrder"][context.user_data["combatOrderIndex"]][2]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write 'Done' to move on to the next entity's turn.")
    return DMCOMBATMENU
