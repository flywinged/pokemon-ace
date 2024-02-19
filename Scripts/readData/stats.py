import csv, typing

from helpers import MAPS

# Pokemon Data container object for the pokemonAdjustments csv
class PokemonData():

    # Expects this to be in a comma separated format without a newline at the end
    def __init__(self, data: typing.List[str]):

        self.index: int = int(data[0])
        self.name: str = data[1]

        # Base Stats
        self.hp: int = int(data[2])
        self.attack: int = int(data[3])
        self.defense: int = int(data[4])
        self.specialAttack: int = int(data[5])
        self.specialDefense: int = int(data[6])
        self.speed: int = int(data[7])
        self.total: int = int(data[8])

        # Types and abilities
        self.type1: str = data[9]
        self.type2: str = data[10]
        if self.type2 == "":
            self.type2 = self.type1
        self.ability: str = data[11]

        # Evolution Information
        self.evolutionInfo: typing.List[typing.Dict[str, str]] = []
        for i in range(12, len(data), 3):
            if data[i] == "": continue

            arg = data[i + 1]
            try: arg = int(arg)
            except: print(f"{arg} could not be converted to int type...")

            self.evolutionInfo.append({
                "eMethod": data[i],
                "eArg": arg,
                "eSpecies": data[i+2]
            })
        
        # Placeholder for moveset information
        self.learnset: typing.List[typing.Tuple[int, str]] = []
    
    def addLearnSet(self, data: typing.Dict[int, typing.List[str]]):
        learnset = []
        for i in range(1, 101):
            if i not in data: continue
            for move in data[i]:
                learnset.append((i, move))
        self.learnset = learnset


    def __str__(self):
        s = self.name + " (" + self.type1 + "/" + self.type2 + ")\n"
        s += "HP:  " + str(self.hp) + "\n"
        s += "ATK: " + str(self.attack) + "\n"
        s += "DEF: " + str(self.defense) + "\n"
        s += "SPD: " + str(self.specialAttack) + "\n"
        s += "SPA: " + str(self.specialDefense) + "\n"
        s += "SPD: " + str(self.speed) + "\n"
        s += "TOT: " + str(self.total) + "\n"
        return s

def _readStats() -> typing.Dict[str, PokemonData]:
    pokemon: typing.Dict[str, PokemonData] = {}
    with open("./data/Stats.tsv", "r", encoding="utf_8_sig") as f:
        lines = f.readlines()[1:]
        for line in lines:
            if line[-1] == "\n":
                line = line[:-1]
            data = line.split("\t")
            if data[8] == "0" : continue

            p = PokemonData(data)
            pokemon[p.name] = p
    
    return pokemon

def _readLearnsets(pokemon: typing.Dict[str, PokemonData]):

    with open("./data/Learnsets.tsv", "r", encoding="utf_8_sig") as f:
        learnsets = {}

        lines = f.readlines()
        for line in lines:
            if line[-1] == "\n": line = line[:-1]
            data = line.split("\t")

            pokemonName = data[0]
            moves = data[1:]

            learnsets[pokemonName] = {}
            for move in moves:
                if move == "": continue
                moveData = move.split("|")
                level, name = int(moveData[0]), moveData[1]
                
                # Massage the name to the correct format
                if name not in MAPS.GAME_TO_INTERNAL:
                    raise Warning(f"{name} not found in moveMap in _ReadLearnsets.")
                name = MAPS.GAME_TO_INTERNAL[name]

                if level not in learnsets[pokemonName]: learnsets[pokemonName][level] = []
                learnsets[pokemonName][level].append(name)

        for p in learnsets:
            moves = False
            for level in learnsets[p]:
                if len(learnsets[p][level]) > 0:
                    moves = True
                    break
            if not moves: continue

            if p not in pokemon:
                print(p)
                raise SyntaxError
            pokemon[p].addLearnSet(learnsets[p])

def readPokemonData() -> typing.Dict[str, PokemonData]:
    pokemon = _readStats()
    _readLearnsets(pokemon)
    return pokemon
