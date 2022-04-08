import Statistics
import Description
import Equipment


class Character:
    stats = Statistics
    #description = Description
    #equipment = Equipment

    def __init__(self, race, clss, stats, description, equipment):
        #self.playerId = playerId,
        self.race = race,
        self.clss = clss,
        self.stats = stats,
        self.description = description,
        self.equipment = equipment

    def getStats(self):
        return self.stats
