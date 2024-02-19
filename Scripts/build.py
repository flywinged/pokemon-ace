import sys

from helpers import download
from HMA import writePythonScriptInHMA, writeHMAScriptInHMA
from readData import readPokemonData, readTrainerData, readIVData, readMoves, readInternalMoves
from updateEncounters import getUpdateEncountersScript
from updatePokemon import writePokemonLearnsets, writeCalculatorPokemonData, getUpdatePokemonScript
from updateTrainers import writeCalculatorTrainerSets, writeIVSpreads, getHMATrainerScripts
from updateItems import setItemEffects, getItemUpdateScript, insertNewItems
from updateMoves import getMoveScripts, updateCalculatorMoves
from updateMechanics import writeCalculatorTypeChart, writeInternalTypeChart

def setup():

    # First, we download all the csv files from drive and store
    # them in the data folder in the root directory
    download()

    # Then we update pokemon learnsets in CFRU as those are required
    # prior to compilation
    pokemonData = readPokemonData()
    writePokemonLearnsets(pokemonData)
    writeCalculatorPokemonData(pokemonData)

    # Ensure all the item scripts have been written and files updated
    insertNewItems()

    # Update the type charts
    writeInternalTypeChart()
    writeCalculatorTypeChart()

    # Handle calculator moves
    readInternalMoves() # This is so we can instantiate the MAPS.SKIPPED_IIDS set
    adjustedMoves = readMoves()
    updateCalculatorMoves(adjustedMoves)

    # We also need to write all the IV data in order to use trainers
    # with IVs on their pokemon. We also will go ahead and write the
    # trainer data to the calculator
    readIVData()
    trainers = readTrainerData()
    writeIVSpreads()
    writeCalculatorTrainerSets(trainers)

    # TODO: Handle the move tables being updated here ".\Complete-Fire-Red-Upgrade\assembly\data\move_tables.s"

    # TODO: Handle moves being updated in the calculator

    # Now we're done with the build setup phase!

def complete():
    
    # Start by simply updating the items according to updateItems
    setItemEffects() # Directly modifies the rom
    scripts = getItemUpdateScript()

    # Then, we want to load in all the data we need. for making
    # all the necessary pokemon changes
    pokemonData = readPokemonData()
    trainers = readTrainerData()
    readIVData()

    # First handle moves
    internalMoves = readInternalMoves()
    adjustedMoves = readMoves()

    # Get a script that only writes things down for moves that have acutally
    # changes from internal -> adjusted.
    scripts += getMoveScripts(internalMoves, adjustedMoves)

    # Then handle pokemon
    scripts += getUpdatePokemonScript(pokemonData)

    # Then encounters
    scripts += getUpdateEncountersScript()

    # Then handle trainers
    scripts += getHMATrainerScripts(trainers)

    # Finally, execute all the scripts back to back
    writeHMAScriptInHMA(["addFairyIcon", "addItems"], False)
    writePythonScriptInHMA(scripts, True)

if __name__ == "__main__":

    # When building the setup command should always go first
    if sys.argv[1] == "setup":
        setup()

    # Complete command always happens after dpe and cfru are built
    elif sys.argv[1] == "complete":
        complete()