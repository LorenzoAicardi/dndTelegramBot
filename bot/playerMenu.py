from telegram import *
from telegram.ext import *
import os
from classes import Character, Dice, Statistics, Equipment
from classes.JSONEncoder import MyEncoder
from classes import Monster

PLAYERMENU, ROLL, PLAYERCOMBATMENU, CHOOSETARGET, ADV, CALCDAMAGE, LVLUP = range(7)


def playerMenu():
    return ConversationHandler(
        entry_points=[CommandHandler('startCampaign', menu)],
        states={
            PLAYERMENU: [MessageHandler(Filters.text &
                                        ~Filters.regex("^Attack|Roll|Rest|Print stats|Print equipment|Quit$|Cast "
                                                       "spell..."), pMenu),
                         MessageHandler(Filters.regex("^Roll$"), roll),
                         MessageHandler(Filters.regex("^Print stats$"), printStats),
                         MessageHandler(Filters.regex("^Print equipment$"), printEquip),
                         MessageHandler(Filters.regex("^Attack$"), playerCombatMenu),
                         MessageHandler(Filters.regex("^Level up$"), levelUp)],
            ROLL: [MessageHandler(Filters.regex("^d4|d6|d8|d12|d20|d100$"), modifier),
                   MessageHandler(Filters.text & ~Filters.regex("^Roll$") &
                                  ~Filters.regex("^d4|d6|d8|d12|d20|d100$"), resolveDie)],
            PLAYERCOMBATMENU: [MessageHandler(Filters.regex("^Attack...$"), attack),
                               MessageHandler(Filters.text & ~Filters.regex("^Attack...$") &
                                              ~Filters.regex("^Quit combat$")
                                              & ~Filters.regex("^Pass...$"), playerCombatMenu),
                               MessageHandler(Filters.regex("^Quit combat$"), pMenu),
                               MessageHandler(Filters.regex("^Pass...$"), passTurn)],
            CHOOSETARGET: [MessageHandler(Filters.text, chooseTarget)],
            ADV: [MessageHandler(Filters.text, adv)],
            CALCDAMAGE: [MessageHandler(Filters.text, calcDamage)],
            LVLUP: [MessageHandler(Filters.text, resolveLvlUp)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)],
        per_chat=True,
        per_user=True
    )


# Only checking if the user is a player
def menu(update: Update, context: CallbackContext):
    if update.message.from_user.id == context.chat_data["activeCampaign"][
        "dm"]:  # So that the DM does not enter the chat.
        context.bot.send_message(chat_id=update.effective_chat.id, text="You're the DM, not a player!")
        return ConversationHandler.END
    if context.bot_data["newCampaign"]:
        context.chat_data["activeCampaign"][update.message.from_user.username + "char"] = \
            context.user_data["activeCampaign"][update.message.from_user.username + "char"]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Write anything to pop up the player menu!")
    return PLAYERMENU


def pMenu(update: Update, context: CallbackContext):  # TODO: MAKE PLAYER EQUIP ARMOR; SO THAT HE GETS RIGHT ARMORCLASS
    keyboard = [[KeyboardButton("Attack")],  # Attack: get a combat menu. Available only if DM started combat.
                [KeyboardButton("Roll")],  # Roll: roll a dice of your choice.
                [KeyboardButton("Rest")],  # Rest: get the option for either a full rest or a short rest.
                [KeyboardButton("Print stats")],  # Prints stats.
                [KeyboardButton("Print equipment")],  # Prints equipment.
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
        # return stato d'uscita
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
    if update.message.text.isnumeric():
        mod = int(update.message.text)
    res = Dice.roll(context.chat_data["chosenDie"], mod)
    context.bot.send_message(chat_id=update.effective_chat.id, text="The result of the die roll is: " + str(res))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


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
    context.chat_data["chosenWeapon"] = update.message.text
    targets = []
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose your target.")
    return ADV


def adv(update: Update, context: CallbackContext):
    context.chat_data["chosenMonster"] = update.message.text
    context.bot.send_message(chat_id=update.effective_chat.id, text="DM, choose if the player has an advantage/"
                                                                    "disadvantage or not. Type 'adv' for advantage, "
                                                                    "'dis' for disadvantage, or 'no' for neither.")
    return CALCDAMAGE


def calcDamage(update: Update, context: CallbackContext):
    adv = update.message.text
    weaponName = context.chat_data["chosenWeapon"]
    monster = context.chat_data["chosenMonster"]
    # for key in context.chat_data["activeCampaign"]:
    #    if key.endswith("monster"):
    #        if context.chat_data["activeCampaign"][key].name == monster:
    #            target = context.chat_data["activeCampaign"][monster + "monster"]

    damage = context.chat_data["activeCampaign"][context.chat_data["currentPlayerKey"]].useWeapon(weaponName, 0)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Damage dealt: " + str(damage))
    if adv == 'adv' or adv == 'Adv':
        hasMissed = context.chat_data["activeCampaign"][monster + "monster"].takeDamageAdv(damage, True)
    elif adv == 'dis' or adv == 'Dis':
        hasMissed = context.chat_data["activeCampaign"][monster + "monster"].takeDamageAdv(damage, False)
    else:
        hasMissed = context.chat_data["activeCampaign"][monster + "monster"].takeDamage(damage)

    context.bot.send_message(chat_id=update.effective_chat.id, text=hasMissed)
    if context.chat_data["activeCampaign"][monster + "monster"].hp <= 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The monster died! "
                                                                        "The players will be granted "
                                                                        "the right amount of xp by the DM. "
                                                                        "The monster has been despawned. ")
        del context.chat_data["activeCampaign"][monster + "monster"]

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
                                                                    + stats)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def printEquip(update: Update, context: CallbackContext):
    equip = Equipment.toString(
        context.chat_data["activeCampaign"][update.message.from_user.username + "char"].equipment)

    update.message.reply_text(text=context.chat_data["activeCampaign"][update.message.from_user.username + "char"].name
                                   + "'s equipment:\n"
                                   + equip)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Type anything to pop up the menu! ")
    return PLAYERMENU


def quitCampaign(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Goodbye " +
                                                                    update.message.from_user.username + "|")
    # context.chat_data["in_conversation"] = False
    return PLAYERMENU
