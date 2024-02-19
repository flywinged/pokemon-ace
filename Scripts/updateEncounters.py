from readData import readEncounters, EncounterData
from HMA import *

import typing

# data.pokemon.wild[0].grass[0].list[0].species = "Bulbasaur"
# data.pokemon.wild[0].grass[0].list[0].lowLevel = "Bulbasaur"
# data.pokemon.wild[0].grass[0].list[0].highLevel = "Bulbasaur"

def getUpdateEncountersScript() -> typing.List[str]:
    encounters = readEncounters()

    script = ""

    # First, we define the function we'll use to find each encounter location
    script += addScriptLine("currentMap = None")
    script += addScriptLine("def setEncounter(bank, id):")
    script += addScriptLine("global currentMap", 1)
    script += addScriptLine("currentMap = None", 1)
    script += addScriptLine("for i in range(len(data.pokemon.wild)):", 1)
    script += addScriptLine("w = data.pokemon.wild[i]", 2)
    script += addScriptLine("if w.bank == bank and w['map'] == id:", 2)
    script += addScriptLine("currentMap = data.pokemon.wild[i]", 3)
    script += addScriptLine("")  

    for e in encounters:
        if e.mapID is None: continue
        if e.level == 0: continue

        script += addScriptLine(f"setEncounter({str(e.mapID[0])}, {str(e.mapID[1])})")
        
        if e.grass[0] != "":
            script += addScriptLine("grass = currentMap.grass[0]")
            script += addScriptLine("grass.rate = 7")
            for i in range(12):
                script += addScriptLine(f"grass.list[{str(i)}].lowLevel = {str(e.level)}")
                script += addScriptLine(f"grass.list[{str(i)}].highLevel = {str(e.level)}")
                script += addScriptLine(f"grass.list[{str(i)}].species = '{e.grass[i]}'")
        
        if e.surf[0] != "":
            script += addScriptLine("surf = currentMap.surf[0]")
            script += addScriptLine("surf.rate = 2")
            for i in range(5):
                script += addScriptLine(f"surf.list[{str(i)}].lowLevel = {str(e.level)}")
                script += addScriptLine(f"surf.list[{str(i)}].highLevel = {str(e.level)}")
                script += addScriptLine(f"surf.list[{str(i)}].species = '{e.surf[i]}'")
        
        if e.fish[0] != "":
            script += addScriptLine("fish = currentMap.fish[0]")
            script += addScriptLine("fish.rate = 20")
            for i in range(5):
                script += addScriptLine(f"fish.list[{str(i)}].lowLevel = {str(e.level)}")
                script += addScriptLine(f"fish.list[{str(i)}].highLevel = {str(e.level)}")
                script += addScriptLine(f"fish.list[{str(i)}].species = '{e.fish[i]}'")
        
        script += "\n"
    
    script += '"Completed Encounters Update Script"'
    return [script]

if __name__ == "__main__":
    scripts = getUpdateEncountersScript()
    writePythonScriptInHMA(scripts)