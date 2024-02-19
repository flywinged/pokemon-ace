import typing
from readData import readPokemonData, PokemonData
from HMA import addScriptLine, writePythonScriptInHMA

def getCalculatorUpdateString(pokemon: PokemonData) -> typing.List[str]:

    if pokemon.name in ["Burmy~2", "Burmy~3"]:
        return []

    name = pokemon.name.replace("Wormadam~3", "Wormadam-Trash")
    name = name.replace("Wormadam~2", "Wormadam-Sandy")
    
    if name == "Nidoran_M": name = "Nidoran-M"
    if name == "Nidoran_F": name = "Nidoran-F"

    data = ["'" + name + "' : {\n"]

    types = [pokemon.type1]
    if pokemon.type2 != pokemon.type1:
        types.append(pokemon.type2)

    typeString = repr(types)
    if len(types) == 1:
        typeString = typeString[:-1] + ", null]"
    
    data.append("\ttypes: " + typeString + ",\n")
    
    baseStats = "\tbs: {"
    baseStats += "hp: " + str(pokemon.hp) + ", "
    baseStats += "at: " + str(pokemon.attack) + ", "
    baseStats += "df: " + str(pokemon.defense) + ", "
    baseStats += "sa: " + str(pokemon.specialAttack) + ", "
    baseStats += "sd: " + str(pokemon.specialDefense) + ", "
    baseStats += "sp: " + str(pokemon.speed) + "},\n"
    data.append(baseStats)
    data.append("\totherFormes: null,\n")

    data.append("\tabilities: {0: '" + pokemon.ability + "'},\n")

    data.append("},\n")
    return data

def writeCalculatorPokemonData(pokemon: typing.Dict[str, PokemonData]):

    calcFileData = None
    with open("./pokemon-calamity-calc/calc/src/data/species.ts", "r", encoding="utf_8_sig") as f:
        calcFileData = f.readlines()

    newCalculatorData = []
    # For each pokemon, format the data accordingly
    for p in pokemon:
        newCalculatorData += getCalculatorUpdateString(pokemon[p])

    # Write the species data back into the calc file
    with open("./pokemon-calamity-calc/calc/src/data/species.ts", "w", encoding="utf_8_sig") as f:

        newData = []

        status = "before"
        for line in calcFileData:
            if status == "before":
                newData.append(line)
                if line == "// BEGIN CUSTOM DATA\n":
                    status = "inside"
                    for l in newCalculatorData:
                        newData.append("\t" + l)
            elif status == "inside" and line == "// END CUSTOM DATA\n":
                status = "outside"
                newData.append(line)
            elif status == "outside":
                newData.append(line)

        f.writelines(newData)

def writeLearnset(fileData: str, pokemon: PokemonData) -> str:
    if len(pokemon.learnset) == 0:
        return fileData

    # TODO: Write data for just 25 moves so that the data can be editted in HMA
    # Modify the function name to reflect this is part of the initial build process. 

    pokemonName = pokemon.name
    if pokemonName == "Flabébé":
        pokemonName = 'Flabebe'
    pokemonName = pokemonName.replace("_", "")
    searchFor = f'static const struct LevelUpMove s{pokemonName}LevelUpLearnset[] = {"{"}\n'
    pokemonLocation = fileData.find(searchFor)
    if pokemonLocation == -1:
        print(pokemonName)
        raise SyntaxError

    pokemonLocation += len(searchFor)
    substring = fileData[pokemonLocation:]
    dataLength = substring.find("};")
    endPokemonLocation = pokemonLocation + dataLength

    # TODO: Something is off here about how the learnset is calculated
    learnsetData = ""
    for move in pokemon.learnset:
        moveName = move[1].upper().replace(" ", "").replace("-", "")

        # Edge cases
        if moveName == "HIJUMPKICK":
            moveName = "HIGHJUMPKICK"
        
        if moveName == "SMELLINGSALT":
            moveName = "SMELLINGSALTS"

        learnsetData += f"\tLEVEL_UP_MOVE({move[0]}, MOVE_{moveName}),\n"
    learnsetData += "\tLEVEL_UP_END,\n"

    return fileData[:pokemonLocation] + learnsetData + fileData[endPokemonLocation:]

def writePokemonLearnsets(pokemon: typing.Dict[str, PokemonData]):
    # FILE_PATH = "./Complete-Fire-Red-Upgrade/src/Tables/level_up_learnsets.c"
    FILE_PATH = "./Dynamic-Pokemon-Expansion/src/Learnsets.c"

    fileData = ""
    with open(FILE_PATH, "r", encoding="utf_8_sig") as f:
        fileData = f.read()
    
    for pokemonName in pokemon:   
        fileData = writeLearnset(fileData, pokemon[pokemonName])
    
    with open(FILE_PATH, "w", encoding="utf_8_sig") as f:
        f.write(fileData)

TYPE_LIST = [
    "Normal", "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel",
    "???", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice", "Dragon", "Dark", "Fairy"
]

def getUpdatePokemonScript(pokemon: typing.Dict[str, PokemonData]) -> typing.List[str]:
    
    script = ""

    # First, we define the function we'll use to find each encounter location
    script += addScriptLine("currentPokemon = None")
    script += addScriptLine("currentPokemonIdx = None")
    script += addScriptLine("def setPokemon(name, idx=1):")
    script += addScriptLine("global currentPokemon", 1)
    script += addScriptLine("global currentPokemonIdx", 1)
    script += addScriptLine("currentPokemon = None", 1)
    script += addScriptLine("for i in range(len(data.pokemon.stats)):", 1)
    script += addScriptLine("p = data.pokemon.names[i]", 2)
    script += addScriptLine("if p.name == name:", 2)
    script += addScriptLine("if idx == 1:", 3)
    script += addScriptLine("currentPokemon = data.pokemon.stats[i]", 4)
    script += addScriptLine("currentPokemonIdx = i", 4)
    script += addScriptLine("break", 4)
    script += addScriptLine("else: idx -= 1", 3)
    script += addScriptLine("") 

    # Now we loop through each pokemon and update their stats accordingly
    for name in pokemon:
        p = pokemon[name]
        name = name.replace("_F", "\sf")
        name = name.replace("_M", "\sm")
        if name == "Flabébé":
            name = 'Flabébé'

        split = name.split("~")
        name = split[0]
        if len(split) > 1:
            script += addScriptLine(f"setPokemon('{name}',{split[1]})")
        else:
            script += addScriptLine(f"setPokemon('{name}')")

        script += addScriptLine("if currentPokemon is not None:")
        script += addScriptLine(f"currentPokemon.hp = {p.hp}", 1)
        script += addScriptLine(f"currentPokemon.attack = {p.attack}", 1)
        script += addScriptLine(f"currentPokemon['def'] = {p.defense}", 1)
        script += addScriptLine(f"currentPokemon.speed = {p.speed}", 1)
        script += addScriptLine(f"currentPokemon.spatk = {p.specialAttack}", 1)
        script += addScriptLine(f"currentPokemon.spdef = {p.specialDefense}", 1)
        script += addScriptLine(f"currentPokemon.type1 = {TYPE_LIST.index(p.type1)}", 1)
        script += addScriptLine(f"currentPokemon.type2 = {TYPE_LIST.index(p.type2)}", 1)
        script += addScriptLine(f"currentPokemon.ability1 = '{p.ability}'", 1)
        script += addScriptLine(f"currentPokemon.ability2 = '{p.ability}'", 1)
        script += addScriptLine("currentPokemon.item1 = '????????'", 1)
        script += addScriptLine("currentPokemon.item2 = '????????'", 1)

        # Reset evolution data
        script += addScriptLine("evoData = data.pokemon.evolutions[currentPokemonIdx]", 1)
        script += addScriptLine("for i in range(1, 17):", 1)
        script += addScriptLine("evoData[f'method{str(i)}'] = 'None'", 2)
        script += addScriptLine("evoData[f'arg{str(i)}'] = 0", 2)
        script += addScriptLine("evoData[f'species{str(i)}'] = '??????'", 2)

        # After Resetting, we want to add our new evolutions in
        for j in range(len(p.evolutionInfo)):
            info = p.evolutionInfo[j]
            script += addScriptLine(f"evoData.method{str(j + 1)} = '{info['eMethod']}'", 1)
            script += addScriptLine(f"evoData.arg{str(j + 1)} = {info['eArg']}", 1)
            script += addScriptLine(f"evoData.species{str(j + 1)} = '{info['eSpecies']}'", 1)
        script += addScriptLine("")

        # TODO: Add evolutions, TMs, and Move Tutors

    script += '"Completed Pokemon Stats Script"'
    return [script]

# Main function which fetches pokemon data and then updates the pokemon data
if __name__ == "__main__":
    
    pokemon = readPokemonData()
    writeCalculatorPokemonData(pokemon)
    writePokemonLearnsets(pokemon)
    scripts = getUpdatePokemonScript(pokemon)
    # print(scripts[0])
    # writePythonScriptInHMA(scripts)