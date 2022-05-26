import telegram
from telegram import *
from telegram.ext import *
from classes import Dice, Statistics
from classes.equipment import Equipment

PLAYERMENU, ROLL, PLAYERCOMBATMENU, CHOOSETARGET, ADV, CALCDAMAGE, LVLUP, RESOLVESPELL, CALCDAMAGEINT = range(9)


def playerMenu():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaign', menu)],
        states={
            PLAYERMENU: [MessageHandler(Filters.text &
                                        ~Filters.regex("^Attack|Roll|Rest|Print stats|Print equipment|Quit|Cast "
                                                       "spell...|Level up$") & ~Filters.command, pMenu),
                         MessageHandler(Filters.regex("^Roll$") & ~Filters.command, roll),
                         MessageHandler(Filters.regex("^Print stats$") & ~Filters.command, printStats),
                         MessageHandler(Filters.regex("^Print equipment$") & ~Filters.command, printEquip),
                         MessageHandler(Filters.regex("^Attack$") & ~Filters.command, playerCombatMenu),
                         MessageHandler(Filters.regex("^Level up$") & ~Filters.command, levelUp),
                         MessageHandler(Filters.regex("^Cast spell...$") & ~Filters.command, castSpell)],
            ROLL: [MessageHandler(Filters.regex("^d4|d6|d8|d12|d20|d100$") & ~Filters.command, modifier),
                   MessageHandler(Filters.text & ~Filters.regex("^Roll$") & ~Filters.command &
                                  ~Filters.regex("^d4|d6|d8|d12|d20|d100$"), resolveDie)],
            PLAYERCOMBATMENU: [MessageHandler(Filters.regex("^Attack...$") & ~Filters.command, attack),
                               MessageHandler(Filters.text & ~Filters.regex("^Attack...$") &
                                              ~Filters.regex("^Quit combat$") &
                                              ~Filters.regex("^Cast spell...$")
                                              & ~Filters.regex("^Pass...$") & ~Filters.command, playerCombatMenu),
                               MessageHandler(Filters.regex("^Quit combat$") & ~Filters.command, pMenu),
                               MessageHandler(Filters.regex("^Pass...$") & ~Filters.command, passTurn),
                               MessageHandler(Filters.regex("^Cast spell...$") & ~Filters.command, castSpell)],
            CHOOSETARGET: [MessageHandler(Filters.text & ~Filters.command, chooseTarget)],
            ADV: [MessageHandler(Filters.text & ~Filters.command, adv)],
            CALCDAMAGE: [MessageHandler(Filters.text & ~Filters.command, calcDamage)],
            LVLUP: [MessageHandler(Filters.text & ~Filters.command, resolveLvlUp)],
            RESOLVESPELL: [MessageHandler(Filters.text & ~Filters.command, resolveSpell)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign), CommandHandler('cancelAction', pMenu)],
        per_chat=True,
        per_user=True
    )


# Only checking if the user is a player
def menu(update: Update, context: CallbackContext):
    if update.message.from_user.id == context.chat_data["activeCampaign"]["dm"]:
        # So that the DM does not enter the chat.
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're the DM, not a player!")
        return ConversationHandler.END
    if context.bot_data["newCampaign"]:
        context.chat_data["activeCampaign"][update.message.from_user.username + "char"] = \
            context.user_data["activeCampaign"][update.message.from_user.username + "char"]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write anything to pop up the player menu! Remember"
                                                                    " that you can use /quit to quit "
                                                                    "the game at any given time.")
    return PLAYERMENU


def pMenu(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("Attack")],  # Attack: get a combat menu. Available only if DM started combat.
                [KeyboardButton("Roll")],  # Roll: roll a dice of your choice.
                [KeyboardButton("Rest")],  # Rest: get the option for either a full rest or a short rest.
                [KeyboardButton("Print stats")],  # Prints stats.
                [KeyboardButton("Print equipment")],  # Prints equipment.
                [KeyboardButton("Level up")],
                [KeyboardButton(
                    "Quit")]]  # Quits campaign. Since per_user=false, essentially it will disable his character.
    if context.chat_data["activeCampaign"][update.message.from_user.username + "char"]._class == "cleric" \
            or context.chat_data["activeCampaign"][update.message.from_user.username + "char"]._class == "wizard":
        keyboard.append([KeyboardButton("Cast spell...")])  # Cast a spell. Only non-offensive spells out of combat.
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return PLAYERMENU


def roll(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("d4")],
                [KeyboardButton("d6")],
                [KeyboardButton("d8")],
                [KeyboardButton("d12")],
                [KeyboardButton("d20")],
                [KeyboardButton("d100")]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose a die to throw.",
                             reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return ROLL


def modifier(update: Update, context: CallbackContext):
    context.chat_data["chosenDie"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="If you want to use a modifier, "
                                                                    "write down the number."
                                                                    " Otherwise, type anything else.")
    return ROLL


def levelUp(update: Update, context: CallbackContext):
    if context.chat_data["activeCampaign"][update.message.from_user.username + "char"].stats.lvlUpPoints == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You can't level up now!")
        return PLAYERMENU
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose 2 statistics to upgrade.")
    return LVLUP


def resolveLvlUp(update: Update, context: CallbackContext):
    chosenStats = update.message.text.split(", ")
    chosenStats[0] = chosenStats[0].strip()
    chosenStats[1] = chosenStats[1].strip()
    chosenStats[0] = chosenStats[0].lower()
    chosenStats[1] = chosenStats[1].lower()
    context.chat_data["activeCampaign"][update.message.from_user.username + "char"].stats.lvlUpStats(chosenStats)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Stats have been upgraded. Use 'print stats' "
                                                                    "to visualize them.")
    return PLAYERMENU


# The mod could be an added value for a check, for example.
def resolveDie(update: Update, context: CallbackContext):
    mod = 0
    if update.message.text.strip().lstrip("-").isnumeric():
        mod = int(update.message.text)
    res = Dice.roll(context.chat_data["chosenDie"], mod)
    resPreMod = res - mod
    context.bot.send_message(chat_id=update.effective_chat.id, text="The result of the die roll is: " + str(resPreMod) +
                             ", the actual result is: " + str(res))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def castSpell(update: Update, context: CallbackContext):
    spells = []
    if "currentPlayer" not in context.chat_data:
        for spell in context.chat_data["activeCampaign"][update.message.from_user.username + "char"].equipment.spells:
            if not hasattr(spell, "damage_type"):
                spells.append([KeyboardButton(spell.name)])
            else:
                spells.append([KeyboardButton(spell.name)])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Select the spell you want to use.",
                             reply_markup=ReplyKeyboardMarkup(spells, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return RESOLVESPELL


def resolveSpell(update: Update, context: CallbackContext):
    chosenSpellName = update.message.text
    result = context.chat_data["activeCampaign"][update.message.from_user.username + "char"].useSpell(chosenSpellName)
    if "currentPlayer" not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text=result[0] + "\nType anything to pull up the menu!")
        return PLAYERMENU
    else:
        if isinstance(result, str):
            context.bot.send_message(chat_id=update.effective_chat.id, text=result + "\nType anything to pull up the menu!")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text= "Type of damage dealt: " + result[0] + ", "
                                     "amount dealt: " + str(result[1]) + ", spell description: " + result[2][0] +
                                     "\nType anything to pull up the menu!")
            return PLAYERCOMBATMENU


def playerCombatMenu(update: Update, context: CallbackContext):
    if "combatOrder" not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're not in combat now.")
        return PLAYERMENU
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="It's " + context.chat_data["currentPlayer"] +
                                                                        "'s turn!")

        actions = [[KeyboardButton("Attack...")], [KeyboardButton("Pass...")], [KeyboardButton("Cast spell...")],
                   [KeyboardButton("Quit combat")]]
        context.bot.send_message(chat_id=update.effective_chat.id, text="Choose what to do next...",
                                 reply_markup=ReplyKeyboardMarkup(actions, one_time_keyboard=True, selective=True),
                                 reply_to_message_id=update.message.message_id)
        return PLAYERCOMBATMENU


def attack(update: Update, context: CallbackContext):
    if "combatOrder" not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The DM has decided to end combat. Type "
                                                                        "anything to return to the player menu.")
        return PLAYERMENU
    if context.chat_data["currentPlayerKey"] != update.message.from_user.username + "char":
        context.bot.send_message(chat_id=update.effective_chat.id, text="It's not your turn yet!")
        return PLAYERCOMBATMENU

    weapons = context.chat_data["activeCampaign"][update.message.from_user.username + "char"].equipment.weapons
    wList = []
    for w in weapons:
        wList.append([KeyboardButton(w.name)])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose your weapon.",
                             reply_markup=ReplyKeyboardMarkup(wList, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return CHOOSETARGET


def chooseTarget(update: Update, context: CallbackContext):
    if "combatOrder" not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The DM has decided to end combat. Type "
                                                                        "anything to return to the player menu.")
        return PLAYERMENU
    context.chat_data["chosenWeapon"] = update.message.text
    targets = []
    for key in context.chat_data["activeCampaign"]:
        if key.endswith("monster"):
            targets.append([KeyboardButton(context.chat_data["activeCampaign"][key].name)])
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose your target.",
                             reply_markup=ReplyKeyboardMarkup(targets, one_time_keyboard=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return ADV


def adv(update: Update, context: CallbackContext):
    if "combatOrder" not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The DM has decided to end combat. Type "
                                                                        "anything to return to the player menu.")
        return PLAYERMENU
    context.chat_data["chosenMonster"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="DM, choose if the player has an advantage/"
                                                                    "disadvantage or not. Type 'adv' for advantage, "
                                                                    "'dis' for disadvantage, or 'no' for neither. Player,"
                                                                    " type the same thing the DM typed, and then"
                                                                    " damage will be calculated.")
    return CALCDAMAGE


def calcDamage(update: Update, context: CallbackContext):  # The target needs to be selected twice to get here... :(
    if "combatOrder" not in context.chat_data:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The DM has decided to end combat. Type "
                                                                        "anything to return to the player menu.")
        return PLAYERMENU
    adv = update.message.text
    adv = adv.strip()
    weaponName = context.chat_data["chosenWeapon"]
    monster = context.chat_data["chosenMonster"]  # MONSTER NAME!!!!! NOT THE MONSTER IDENTIFIER!!!!
    target = ""
    for key in context.chat_data["activeCampaign"]:
        if key.endswith("monster"):
            if context.chat_data["activeCampaign"][key].name == monster:
                print("gets here")  # does not get here!
                target = context.chat_data["activeCampaign"][key]  # FOUND THE IDENTIFIER HERE

    if target == "":
        context.bot.send_message(chat_id=update.effective_chat.id, text="We haven't found the monster. Retry,"
                                                                                " it's still your turn. ")
        return PLAYERCOMBATMENU

    damage = context.chat_data["activeCampaign"][context.chat_data["currentPlayerKey"]].useWeapon(weaponName, 0)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Damage dealt: " + str(damage))
    if adv == 'adv' or adv == 'Adv':
        hasMissed = target.takeDamageAdv(damage, True)
    elif adv == 'dis' or adv == 'Dis':
        hasMissed = target.takeDamageAdv(damage, False)
    else:
        hasMissed = target.takeDamage(damage)

    context.bot.send_message(chat_id=update.effective_chat.id, text=hasMissed)
    if target.hp <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The monster died! "
                                                                        "The players will be granted "
                                                                        "the right amount of xp by the DM. "
                                                                        "The monster has been despawned. ")
        del target

    context.chat_data["combatOrderIndex"] = context.chat_data["combatOrderIndex"] + 1
    if context.chat_data["combatOrderIndex"] == len(context.chat_data["combatOrder"]):
        context.chat_data["combatOrderIndex"] = 0
    context.chat_data["currentPlayer"] = context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][0]
    context.chat_data["currentPlayerKey"] = context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][2]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Write 'Done' to move on to the next entity's turn.")
    return PLAYERCOMBATMENU


def passTurn(update: Update, context: CallbackContext):
    if context.chat_data["currentPlayerKey"] != update.message.from_user.username + "char":
        context.bot.send_message(chat_id=update.effective_chat.id, text="It's not your turn yet!")
        return PLAYERCOMBATMENU

    context.chat_data["combatOrderIndex"] = context.chat_data["combatOrderIndex"] + 1
    if context.chat_data["combatOrderIndex"] == len(context.chat_data["combatOrder"]):
        context.chat_data["combatOrderIndex"] = 0
    context.chat_data["currentPlayer"] = context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][0]
    context.chat_data["currentPlayerKey"] = context.chat_data["combatOrder"][context.chat_data["combatOrderIndex"]][2]
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Write 'Done' to move on to the next entity's turn.")
    return PLAYERCOMBATMENU


def printStats(update: Update, context: CallbackContext):
    stats = Statistics.toString(context.chat_data["activeCampaign"][update.message.from_user.username + "char"].stats)
    context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data["activeCampaign"][
                                                                        update.message.from_user.username + "char"].name + "'s stats:\n"
                                                                    + stats,
                             parse_mode=telegram.ParseMode.HTML)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def printEquip(update: Update, context: CallbackContext):
    equip = Equipment.toString(
        context.chat_data["activeCampaign"][update.message.from_user.username + "char"].equipment)

    update.message.reply_text(text=context.chat_data["activeCampaign"][update.message.from_user.username + "char"].name
                                   + "'s equipment:\n"
                                   + equip, parse_mode=telegram.ParseMode.HTML)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def quitCampaign(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Goodbye " +
                                                                    update.message.from_user.username + "!")
    return PLAYERMENU
