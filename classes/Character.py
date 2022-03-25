
import random
from random import choice
import json
import numpy as np

#with open("C:/Users/loren/Desktop/Università/3° anno/Progetto di ingegneria informatica/dndTelegramBot/resources/equipment.json", "r") as read_file:
    #races = json.load(read_file)

def statistics(race, cla) -> int:

    res = []
    att = []
    strength = 0
    dex = 0
    constitution = 0
    intelligence = 0
    charisma = 0
    wisdom = 0
    if race == "dwarf": #change in statistics due to race choice
        constitution + 2
    if race == "elf":

    if race == "halfling":

    if race == "human":


    for j in range(6):
        for i in range(4):
            res[i] = random.randint(1,6)
        np.sort(res)
        att[j] = res[1] + res[2] + res[3]