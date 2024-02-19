import csv
import typing

# Container for all the information about a specific map/route encounters
class EncounterData:

    def __init__(self, data: typing.List[str]):

        # Identifying information first
        headerSplit = data[0].split("|")
        self.mapID: typing.Tuple[int, int] = None
        if headerSplit[0] != "None": self.mapID = tuple(map(lambda x: int(x), headerSplit[0].split("-")))
        self.mapName: str = headerSplit[1]

        # Then we fetch level data
        self.level: int = int(data[1])

        # And finally we fetch grass/surf/fishing data
        self.grass: typing.List[str] = []
        for i in range(3, 15): self.grass.append(data[i])

        self.surf: typing.List[str] = []
        for i in range(16, 21): self.surf.append(data[i])

        self.fish: typing.List[str] = []
        for i in range(22, 27): self.fish.append(data[i])
    
    def __str__(self):
        string = ""
        string += f"{str(self.mapID)} - {self.mapName}\n"
        string += f"Level: {str(self.level)}\n"
        string += f"Grass: {str(self.grass)}\n"
        string += f"Surf: {str(self.surf)}\n"
        string += f"Gish: {str(self.fish)}\n"
        return string

def readEncounters() -> typing.List[EncounterData]:

    encounterData = []
    with open("./data/Encounters.tsv", "r", encoding="utf_8_sig") as f:
        for line in f.readlines():
            if line[-1] == "\n": line = line[:-1]
            splitLine = line.split("\t")
            for i in range(max(len(splitLine), len(encounterData))):
                if i >= len(encounterData):
                    encounterData.append([])
                
                if i >= len(splitLine):
                    encounterData[i].append("")
                else:
                    encounterData[i].append(splitLine[i])
    
    encounterData = encounterData[3:]
    encounters = list(map(lambda x: EncounterData(x), encounterData))
    return encounters