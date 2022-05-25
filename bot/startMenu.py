import json
import re

import telegram
from telegram import *
from telegram.ext import *
import os
from classes import Character, Statistics, Monster, Equipment, Wealth, Weapon, Armor, Adv_Gear, Pack, Spell, Tool
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
    startingMenu = [[KeyboardButton("New campaign")], [KeyboardButton("Load campaign")]]
    context.bot.send_message(chat_id=context.bot_data["Group chat id"],
                             text="Welcome! Choose whether you want to start a new campaign "
                                  "or load an older one. ",
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
        print("here")
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
    if not os.path.isdir(path) or not os.listdir():
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

                # initialize weapons
                weapons = []
                for w in campaign[key]["equipment"]["weapons"]:
                    properties = []
                    for prop in w["properties"]:
                        properties.append(prop)
                    wp = Weapon.Weapon(w["name"], Wealth.Wealth(0, 0, 0, w["cost"]["gp"], 0), w["damage_dice"],
                                       w["damage_type"], w["weight"], properties)
                    weapons.append(wp)
                # initialize armor
                armor = []
                for a in campaign[key]["equipment"]["armor"]:
                    arm = Armor.Armor(a["name"], Wealth.Wealth(0, 0, 0, a["cost"]["gp"], 0), a["armorClass"],
                                      a["strength"], a["weight"])
                    armor.append(arm)
                # initialize advGear
                advGear = []
                for ad in campaign[key]["equipment"]["advGear"]:
                    if ad["gear_category"] == "Equipment Packs":
                        adv = Pack.Pack(ad["name"], Wealth.Wealth(0, 0, 0, ad["cost"]["gp"], 0), ad["gear_category"],
                                        ad["contents"])
                    else:
                        adv = Adv_Gear.Adv_Gear(ad["name"], ad["gear_category"]["name"],
                                                Wealth.Wealth(0, 0, 0, ad["cost"]["gp"], 0),
                                                ad["weight"])
                    advGear.append(adv)
                # initialize spells
                spells = []
                if campaign[key]["_class"] == "cleric" or campaign[key]["_class"] == "wizard":
                    for s in campaign[key]["equipment"]["spells"]:
                        if "damage_dice" in s:
                            spell = Spell.loadSpell(s["name"], s["level"], s["classes"], s["desc"], s["damage_type"],
                                                    s["damage_dice"])
                        else:
                            spell = Spell.loadSpell(s["name"], s["level"], s["classes"], s["desc"], None,
                                                    None)
                        spells.append(spell)

                # initialize tools
                tools = []
                for t in campaign[key]["equipment"]["tools"]:
                    tool = Tool.Tool(t["name"], t["tool_cat"], Wealth.Wealth(0, 0, 0, t["cost"]["gp"], 0), t["weight"])
                    tools.append(tool)

                equipment = Equipment.Equipment(Wealth.Wealth(
                    campaign[key]["equipment"]["wealth"]["cp"],
                    campaign[key]["equipment"]["wealth"]["sp"],
                    campaign[key]["equipment"]["wealth"]["ep"], campaign[key]["equipment"]["wealth"]["gp"],
                    campaign[key]["equipment"]["wealth"]["pp"]
                ),
                    armor, weapons,
                    campaign[key]["equipment"]["spellCast"],
                    advGear, tools,
                    spells)
                character = Character.loadChar(campaign[key]["playerID"], campaign[key]["name"], campaign[key]["race"],
                                               campaign[key]["_class"], stats, equipment)
                context.chat_data["activeCampaign"][key] = character
            else:
                monsterNames = []
                for k in context.chat_data["activeCampaign"]:
                    if k.endswith("monster"):
                        name = "".join(re.split('[^a-zA-Z]*', context.chat_data["activeCampaign"][k].name))
                        monsterNames.append(name)

                monster = Monster.loadMonster(
                    campaign[key]["name"], campaign[key]["hp"], campaign[key]["hd"],
                    campaign[key]["speed"], campaign[key]["strength"], campaign[key]["dex"],
                    campaign[key]["const"], campaign[key]["intl"], campaign[key]["wis"],
                    campaign[key]["cha"], campaign[key]["proficiencies"],
                    campaign[key]["senses"], campaign[key]["languages"], campaign[key]["challenge"],
                    campaign[key]["actions"], campaign[key]["damage_vulnerabilities"],
                    campaign[key]["damage_resistances"], campaign[key]["damage_immunities"])
                context.chat_data["activeCampaign"][key] = monster

                if monster.name not in monsterNames:
                    context.chat_data[monster.name + "sameNameCounter"] = 0
                    context.chat_data["activeCampaign"][monster.name + "monster"] = monster
                    nameOfSpawnedMonster = context.chat_data["activeCampaign"][monster.name + "monster"].name
                else:
                    monsterIndex = context.chat_data[monster.name + "sameNameCounter"]
                    monsterIndex = monsterIndex + 1
                    context.chat_data[monster.name + "sameNameCounter"] = monsterIndex

    context.chat_data["activeCampaign"]["dm"] = campaign["dm"]
    context.bot_data["campaignName"] = update.message.text  # save campaign name so that I know where to save data.
    context.bot.send_message(chat_id=update.effective_chat.id, text="Campaign loaded! Enter /startCampaign to begin.\n"
                                                                    "DM, enter /startCampaignDM to open up your menu.")
    return ConversationHandler.END


def quitCampaign(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    context.chat_data.clear()
    context.bot_data.clear()
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you next time!")
    return ConversationHandler.END

