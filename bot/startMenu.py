import json

import telegram
from telegram import *
from telegram.ext import *
import os
from classes import Character, Statistics, Monster, Equipment, Wealth
from . import charCreationMenu

# equipLoop = "^Mace$|^Warhammer$|^Scale Mail$|^Leather Armor$|^Chain Mail$|^Leather Armor$|^Longbow$|^Martial " \
#             "Weapon$|^Shield$|^Martial Weapon$|^Light Crossbow$|^Handaxe$|^Dungeoneer's Pack$|^Explorer's " \
#             "Pack$|^Rapier$|^Shortbow$|^Shortsword$||^Burglar's Pack$|^Dagger$|^Thieves' " \
#             "Tools$|^Quarterstaff$|^Component Pouch$|^Arcane Focus$|^Scholar's Pack$|^Spellbook$"

CAMPAIGN, NEWCAMP, LOADCAMP, CHARCREATION = range(4)

cwd = os.getcwd()


def start_cmd():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CAMPAIGN: [MessageHandler(Filters.regex('^New campaign$') & ~Filters.command, newCampaign),
                       MessageHandler(Filters.regex('^Load campaign$') & ~Filters.command, loadCampaign)],
            NEWCAMP: [MessageHandler(Filters.text, setDM)],
            LOADCAMP: [MessageHandler(Filters.text, loadCamp)],
            CHARCREATION: [MessageHandler(Filters.text, charCreation)]
        },
        fallbacks=[CommandHandler('quit', quitCampaign)],
        per_user=False,
        per_chat=True
    )


def start(update: Update, context: CallbackContext) -> int:
    context.bot_data["Group chat id"] = update.effective_chat.id
    if "activeCampaign" in context.chat_data:  # THIS FUCKING WORKS
        print(context.bot_data["activeCampaign"])
    startingMenu = [[KeyboardButton("New campaign")], [KeyboardButton("Load campaign")]]
    context.bot.send_message(chat_id=context.bot_data["Group chat id"],
                             text="Choose whether you want to start a new campaign"
                                  "or load an older one.",
                             reply_markup=ReplyKeyboardMarkup(startingMenu, one_time_keyboard=True))
    return CAMPAIGN


def newCampaign(update: Update, context: CallbackContext) -> int:
    context.bot_data["newCampaign"] = True
    context.bot.send_message(chat_id=update.effective_chat.id, text="Alright, a new campaign! What should we name it?")
    return NEWCAMP


def setDM(update: Update, context: CallbackContext) -> int:
    path = cwd + "/campaigns"
    if not os.path.isdir(path):
        os.mkdir(path)
    os.chdir(path)
    context.bot_data["campaignName"] = update.message.text
    open(context.bot_data["campaignName"] + ".json", "x")  # creates the json file with the campaign
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your campaign has been created successfully! "
                                                                    "The next user that writes a message will be "
                                                                    "the DM.")
    return CHARCREATION


def charCreation(update: Update, context: CallbackContext) -> int:
    context.chat_data["activeCampaign"] = dict()
    context.chat_data["activeCampaign"]["dm"] = update.message.from_user.username
    dm = {"dm": context.chat_data["activeCampaign"]["dm"]}
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_message.from_user.username
                                                                    + "is the Dungeon Master for "
                                                                      "this campaign.")
    with open(context.bot_data["campaignName"] + ".json", "a") as cmp:
        json.dump(dm, cmp, indent=4)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Players may type the command /createChar"
                                                                    " to create a new character, and DM may type "
                                                                    " /startCampaignDM to open up his menu once "
                                                                    " everyone is done.")
    return ConversationHandler.END


############LOAD CAMPAIGN##############


def loadCampaign(update: Update, context: CallbackContext) -> int:
    context.bot_data["newCampaign"] = False
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
        replyK.append([KeyboardButton(cmp[:len(cmp) - 5])])  # last five characters are ".json"
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose the campaign you want to load!",
                             reply_markup=ReplyKeyboardMarkup(replyK, one_time_keyboard=True))
    return LOADCAMP


def loadCamp(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Loading campaign...")
    with open(update.message.text + ".json", "r") as cmp:
        campaign = json.load(cmp)
    context.chat_data["activeCampaign"] = dict()
    for key in campaign:
        if key != "dm":
            if key.endswith("char"):
                stats = Statistics.loadStats(
                    campaign[key]["stats"]["lvl"],
                    campaign[key]["stats"]["xp"], campaign[key]["stats"]["ins"], campaign[key]["stats"]["profBonus"],
                    campaign[key]["stats"]["initiative"], campaign[key]["stats"]["speed"], campaign[key]["stats"]["hp"],
                    campaign[key]["stats"]["hd"],
                    campaign[key]["stats"]["max_hd"], campaign[key]["stats"]["strMod"],
                    campaign[key]["stats"]["dexMod"], campaign[key]["stats"]["constMod"],
                    campaign[key]["stats"]["intlMod"], campaign[key]["stats"]["wisMod"],
                    campaign[key]["stats"]["chaMod"], campaign[key]["stats"]["hd_number"],
                    campaign[key]["stats"]["lvlUpPoints"], campaign[key]["stats"]["strength"],
                    campaign[key]["stats"]["dex"], campaign[key]["stats"]["const"],
                    campaign[key]["stats"]["intl"], campaign[key]["stats"]["wis"], campaign[key]["stats"]["cha"],
                    campaign[key]["stats"]["spell_slots"],
                    campaign[key]["stats"]["curr_used_spell_slots"], campaign[key]["stats"]["damage_vulnerabilities"],
                    campaign[key]["stats"]["damage_resistances"], campaign[key]["stats"]["damage_immunities"]
                )
                equipment = Equipment.Equipment(Wealth.Wealth(
                    campaign[key]["equipment"]["wealth"]["cp"],
                    campaign[key]["equipment"]["wealth"]["sp"],
                    campaign[key]["equipment"]["wealth"]["ep"], campaign[key]["equipment"]["wealth"]["gp"],
                    campaign[key]["equipment"]["wealth"]["pp"]
                ),
                    campaign[key]["equipment"]["armor"], campaign[key]["equipment"]["weapons"],
                    campaign[key]["equipment"]["spellCast"],
                    campaign[key]["equipment"]["advGear"], campaign[key]["equipment"]["tools"],
                    campaign[key]["equipment"]["spells"])
                character = Character.loadChar(campaign[key]["playerID"], campaign[key]["name"], campaign[key]["race"],
                                               campaign[key]["_class"], stats, equipment)
                context.chat_data["activeCampaign"][update.message.from_user.username + "char"] = character
            else:
                monster = Monster.loadMonster(
                    campaign[key]["name"], campaign[key]["hp"], campaign[key]["hd"],
                    campaign[key]["speed"], campaign[key]["strength"], campaign[key]["dex"],
                    campaign[key]["const"], campaign[key]["intl"], campaign[key]["wis"],
                    campaign[key]["cha"], campaign[key]["proficiencies"],
                    campaign[key]["senses"], campaign[key]["languages"], campaign[key]["challenge"],
                    campaign[key]["actions"], campaign[key]["damage_vulnerabilities"],
                    campaign[key]["damage_resistances"], campaign[key]["damage_immunities"])
                context.chat_data["activeCampaign"][monster.name + "monster"] = monster
            # IT WORKS! Now I need to put them in their spots and to assign them to the correct players.
            # The convention is that characters end with "char" and monsters end with "monster", so that
            # it's easier for me to save them in memory.
    context.chat_data["activeCampaign"]["dm"] = campaign["dm"]
    context.chat_data["campaignName"] = update.message.text  # save campaign name so that I know where to save data.
    context.bot.send_message(chat_id=update.effective_chat.id, text="Campaign loaded! Enter /startCampaign to begin.\n"
                                                                    "DM, enter /startCampaignDM to open up your menu.")
    return ConversationHandler.END


def quitCampaign(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    context.chat_data.clear()
    context.bot_data.clear()
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you next time!")
    return ConversationHandler.END

    # TODO: should be a RETURN GAMESTATE or whatever I decide to call the menu when the game starts
