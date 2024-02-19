import typing, json
from helpers import MAPS, toID

class IVSpread:

    MAP = {}
    index = 1

    def __init__(self, data: typing.List[str]):
        self.name: str = data[0]
        self.nature: str = data[1]
        self.ivs: int = int(data[2])
        self.hp: int = 4 * int(data[3])
        self.at: int = 4 * int(data[4])
        self.df: int = 4 * int(data[5])
        self.sa: int = 4 * int(data[6])
        self.sd: int = 4 * int(data[7])
        self.sp: int = 4 * int(data[8])
        self.index = IVSpread.index

        IVSpread.MAP[self.name] = self
        IVSpread.index += 1

class TrainerData:
    def __init__(self, data: typing.List[typing.List[str]]):
        self.name: str = data[0][0]
        self.itemList: typing.List[str] = data[0][1].split(" - ")
        self.battleType: str = data[0][2]
        self.pokemon: typing.List[TrainerPokemonData] = []
        for dataRow in data:
            try:
                self.pokemon.append(TrainerPokemonData(self.name, dataRow))
            except:
                Warning("Invalid trainer data passed in:", data)
    
    def __str__(self):
        s = self.name + "\n"
        for p in self.pokemon:
            s += str(p)
        return s


class TrainerPokemonData:
    POKEMON_INDEX = 0

    def __init__(self, trainer: str, data: typing.List[str]):
        
        self.trainer: str = trainer
        self.name: str = data[3]
        self.index: int = TrainerPokemonData.POKEMON_INDEX
        TrainerPokemonData.POKEMON_INDEX += 1

        self.level: int = int(data[4])
        self.ivSpread: str = data[5]
        self.ability: str = data[6]
        self.item: str = data[7]

        self.moves: typing.List[str] = [data[8]]
        for i in range(3):
            if 9 + i >= len(data): continue
            gameName = data[9 + i]
            if gameName != "":
                if gameName not in MAPS.GAME_TO_CALC:
                    raise Warning(f"{gameName} not found in MAPS.GAME_TO_CALC during TrainerPokemonData.__init__()")
                calcName = MAPS.GAME_TO_CALC[gameName]
                self.moves.append(calcName)
            else:
                self.moves.append("-")
    
    def __str__(self):
        spread: IVSpread = IVSpread.MAP[self.ivSpread]
        s = self.trainer + " - " + self.name + " @ " + self.item + "\n"
        s += str(self.level) + " - " + spread.nature + "\n"
        s += str(self.moves) + "\n"
        return s

    def createCodeString(self):        
        if self.ivSpread not in IVSpread.MAP:
            print(self)
            raise SyntaxError
        
        ivData: IVSpread = IVSpread.MAP[self.ivSpread]

        moves = []
        for m in self.moves:
            if m != "-":
                moves.append(m)

        data = {
            self.trainer : {
                "level" : self.level,
                "ability" : self.ability,
                "moves" : moves,
                "nature" : ivData.nature,
                "evs": {
                    "hp": ivData.hp,
                    "at": ivData.at,
                    "df": ivData.df,
                    "sa": ivData.sa,
                    "sd": ivData.sd,
                    "sp": ivData.sp
                },
                "ivs": {
                    "hp": ivData.ivs,
                    "at": ivData.ivs,
                    "df": ivData.ivs,
                    "sa": ivData.ivs,
                    "sd": ivData.ivs,
                    "sp": ivData.ivs
                },
                "item" : self.item,
                "index" : self.index,
            }
        }
        return json.dumps(data, indent=4)


# Read in all the data from the ivSpreads.tsv File
def readIVData():
    IVSpread("00000,Serious,0,0,0,0,0,0,0,0".split(","))
    IVSpread("11111,Serious,31,23,21,21,21,21,21,128".split(","))
    with open("./data/ivSpreads.tsv", "r", encoding="utf_8_sig") as f:
        lines = f.readlines()[1:]
        for data in lines:

            if data[-1] == "\n": data = data[:-1]
            dataSplit = data.split("\t")
            if dataSplit[0] == "":
                continue

            IVSpread(dataSplit)


# Read in all the data from the pokemonAdjustments.tsv file
def readTrainerData() -> typing.List[TrainerData]:
    trainers: typing.List[TrainerData] = []
    with open("./data/Trainers.tsv", "r", encoding="utf_8_sig") as f:
        lines = f.readlines()[1:]

        trainerData: typing.List[typing.List[str]] = []
        for data in lines:

            if data[-1] == "\n": data = data[:-1]
            dataSplit = data.split("\t")

            if dataSplit[0] != "":
                if len(trainerData) > 0:
                    td = TrainerData(trainerData)
                    if len(td.pokemon) > 0:
                        trainers.append(td)
                    trainerData = []
            trainerData.append(dataSplit)
        
        if len(trainerData) > 0:
            td = TrainerData(trainerData)
            if len(td.pokemon) > 0:
                trainers.append(td)
    
    return trainers