from HMA import addScriptLine
from readData import readIVData, readTrainerData
from helpers import MAPS

import typing
import helpers

from readData import TrainerData, TrainerPokemonData, IVSpread

from HMA import writePythonScriptInHMA

def chopBrackets(s: str):
    lines = s.split("\n")
    return "\n".join(lines[1:-1])

def writeCalculatorTrainerSets(trainers: typing.List[TrainerData]):
    pokemonMap: typing.Dict[str, typing.List[TrainerPokemonData]] = {}
    for trainer in trainers:
        for pokemon in trainer.pokemon:
            if pokemon.name not in pokemonMap:
                pokemonMap[pokemon.name] = []
            pokemonMap[pokemon.name].append(pokemon)
    
    with open("./pokemon-calamity-calc/src/js/data/sets/gen8.js", "w", encoding="utf_8_sig") as f:
        data = "var SETDEX_SS = {\n"

        for pokemonName in pokemonMap:

            # This is to fix some stupid issue with the character encodings
            name = pokemonName
            if pokemonName == "Flabébé":
                name = "Flabébé"

            data += "    " + name + ":  {\n"
            pokemonList = pokemonMap[pokemonName]
            for p in pokemonList:
                codeString = p.createCodeString()
                codeString = helpers.indentString(codeString)
                data += chopBrackets(codeString) + ",\n"
            data += "    },\n"

        data += "}"
        f.write(data)

def insertSpreadsData(data: str, insertData: IVSpread) -> str:

    startKey = "[0] = {0}, //Empty Spread\n"
    endKey = "\t},\n};\n#endif"

    start = data.index(startKey) + len(startKey)
    end = data.index(endKey)

    return data[:start] + insertData + data[end:]

def getSpreadString(spread: IVSpread) -> str:
    data = ""

    data += f"\t[{str(spread.index)}] =\n"
    data += "\t{ // " + spread.name + "\n"
    data += f"\t\t.nature = NATURE_{spread.nature.upper()},\n"
    data += f"\t\t.ivs = {str(spread.ivs)},\n"
    data += f"\t\t.hpEv = {str(spread.hp)},\n"
    data += f"\t\t.atkEv = {str(spread.at)},\n"
    data += f"\t\t.defEv = {str(spread.df)},\n"
    data += f"\t\t.spdEv = {str(spread.sp)},\n"
    data += f"\t\t.spAtkEv = {str(spread.sa)},\n"
    data += f"\t\t.spDefEv = {str(spread.sd)},\n"
    data += "\t\t.ball = TRAINER_EV_CLASS_BALL,\n"
    data += "\t\t.ability = Ability_1,\n"
    data += "\t},\n"

    return data

def writeIVSpreads():
    if len(IVSpread.MAP) == 0:
        raise Exception("readIVData not called before writeIVSpreads().")
    
    data = None
    with open("./Complete-Fire-Red-Upgrade/src/Tables/trainers_with_evs_table.h", "r", encoding="utf_8_sig") as f:
        data = f.read()
    
    # Accumulate new insert data
    insertData = ""
    for name in sorted(list(IVSpread.MAP)):
        spread = IVSpread.MAP[name]
        insertData += getSpreadString(spread)

    insertData = insertData[:-4]
    data = insertSpreadsData(data, insertData)

    with open("./Complete-Fire-Red-Upgrade/src/Tables/trainers_with_evs_table.h", "w", encoding="utf_8_sig") as f:
        f.write(data)

def getHMATrainerScripts(trainers: typing.List[TrainerData]):
    # 743 Trainers to play with

    if len(trainers) == 0:
        return []

    # We will do this by generating a python script which will be run on the HMA utility
    scriptStart = ""

    scriptStart += addScriptLine("trainerData = None")
    scriptStart += addScriptLine("def getTrainer(name):")
    scriptStart += addScriptLine("global trainerData", 1)
    scriptStart += addScriptLine("trainerData = None", 1)
    scriptStart += addScriptLine("for i in range(len(data.trainers.stats)):", 1)
    scriptStart += addScriptLine("t = data.trainers.stats[i]", 2)
    scriptStart += addScriptLine("if t.name == name:", 2)
    scriptStart += addScriptLine("trainerData = data.trainers.stats[i]", 3)
    scriptStart += addScriptLine("") 

    scriptEnd = scriptStart

    for trainer in trainers:
        scriptStart += f"getTrainer('{trainer.name}')\n"
        scriptStart += f"trainerData.name = '{trainer.name}'\n"
        scriptStart += f"trainerData.structType = 'Both'\n"

        if len(trainer.itemList) > 0:
            itemCount = 1
            for item in trainer.itemList:
                if item:
                    scriptStart += f"trainerData.item{itemCount} = '{item.upper()}'\n"
                    itemCount += 1
        
        scriptStart += f"trainerData.doubleBattle = '{trainer.battleType}'\n"
        if trainer.battleType == "Double":
            scriptStart += f"trainerData.ai.DoubleBattle = 1\n"
        scriptStart += f"trainerData.pokemonCount = {len(trainer.pokemon)}\n"

        # TODO: Add trainerData.ai.[X] options to be the same for all trainers.
        scriptStart += f"trainerData.ai.CheckBadMove = 1\n"
        scriptStart += f"trainerData.ai.TryToKO = 1\n"
        scriptStart += f"trainerData.ai.CheckViability = 1\n"

        scriptStart += "\n"

        EASY_MODE = False

        for j in range(len(trainer.pokemon)):
            pokemon = trainer.pokemon[j]

            moves = list(map(lambda x: MAPS.CALC_TO_GAME[x], pokemon.moves))
            while len(moves) < 4:
                moves.append("-")
            
            if EASY_MODE: pokemon.level = 1

            pokemonName = pokemon.name
            if pokemonName == "Flabébé":
                pokemonName = 'Flabébé'

            scriptEnd += f"getTrainer('{trainer.name}')\n"
            scriptEnd += f"trainerData.pokemon[{j}].level = {pokemon.level}\n"
            scriptEnd += f"trainerData.pokemon[{j}].mon = '{pokemonName.upper()}'\n"
            scriptEnd += f"trainerData.pokemon[{j}].ivSpread = {IVSpread.MAP[pokemon.ivSpread].index}\n"
            scriptEnd += f"trainerData.pokemon[{j}].item = '{pokemon.item.upper()}'\n"
            scriptEnd += f"trainerData.pokemon[{j}].move1 = '{moves[0]}'\n"
            scriptEnd += f"trainerData.pokemon[{j}].move2 = '{moves[1]}'\n"
            scriptEnd += f"trainerData.pokemon[{j}].move3 = '{moves[2]}'\n"
            scriptEnd += f"trainerData.pokemon[{j}].move4 = '{moves[3]}'\n"
        
        scriptEnd += "\n"

    scriptStart += '"Completed Trainer Start Script"'
    scriptEnd += '"Completed Trainer End Script"'
    return [scriptStart, scriptEnd]

if __name__ == "__main__":

    readIVData()
    trainers = readTrainerData()
    
    writeCalculatorTrainerSets(trainers)

    scripts = getHMATrainerScripts(trainers)
    writePythonScriptInHMA(scripts)
    
