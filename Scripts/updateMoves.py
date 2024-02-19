import typing
from readData import MoveData, readMoves, readInternalMoves
from helpers import MAPS, toID, IGNORE_MOVES
from HMA import addScriptLine, writePythonScriptInHMA

TARGET_MAP = {
    'TARGET_SELECTED':        0x0,
    'TARGET_DEPENDS':         0x1,
    'TARGET_USER_OR_PARTNER': 0x2,
    'TARGET_RANDOM':          0x4,
    'TARGET_BOTH':            0x8,
    'TARGET_USER':            0x10,
    'TARGET_FOES_AND_ALLY':   0x20,
    'TARGET_ALL':   		  0x20,
    'TARGET_OPPONENTS_FIELD': 0x40
}

def _moveUpdateString(internalMove: MoveData, adjustedMove: MoveData) -> str:
    string = ""

    string += addScriptLine(f'setMove("{adjustedMove.name}")')
    string += addScriptLine("if currentMove is not None:")

    def checkAndApply(field: str, quotes: bool) -> str:
        internalValue, adjustedValue = getattr(internalMove, field), getattr(adjustedMove, field)
        if internalValue != adjustedValue and adjustedValue is not None:
            value = getattr(adjustedMove, field)

            # Handle a couple simple edge cases
            if field == "target":
                value = TARGET_MAP['TARGET_' + value]
            target = "currentMove" if field != "description" else "currentMoveDescription"

            if field == "description":
                value = value.replace("\\n", "\\\\n")

            # Return the script line based on if quotes are required or not
            if quotes:
                return addScriptLine(f'{target}.{field} = "{value}"', 1)
            else:
                return addScriptLine(f'{target}.{field} = {value}', 1)
        
        else:
            return ""

    string += checkAndApply("description", True)
    string += checkAndApply("effect", True)
    string += checkAndApply("type", True)
    string += checkAndApply("power", False)
    string += checkAndApply("accuracy", False)
    string += checkAndApply("pp", False)
    string += checkAndApply("effectAccuracy", False)
    string += checkAndApply("priority", False)
    string += checkAndApply("target", False)
    if string.count("\n") == 2:
        string = string[:-1]
        string += addScriptLine(" pass")
    
    string += addScriptLine(f'else: failedMoves.append("{adjustedMove.name}")')
    string += "\n"
    
    return string

def getMoveScripts(
        internalMoves: typing.Dict[str, MoveData],
        adjustedMoves: typing.Dict[str, MoveData]
) -> typing.List[str]:

    script = ""

    # Write the function that locates the correct move
    script += addScriptLine("failedMoves = []")
    script += addScriptLine("currentMove = None")
    script += addScriptLine("lastIdx = 0")
    script += addScriptLine("currentMoveDescription = None")
    script += addScriptLine("def setMove(name):")
    script += addScriptLine("global currentMove", 1)
    script += addScriptLine("global currentMoveDescription", 1)
    script += addScriptLine("global lastIdx", 1)
    script += addScriptLine("currentMove = None", 1)
    script += addScriptLine("for i in range(lastIdx, len(data.pokemon.moves.names)):", 1)
    script += addScriptLine("if data.pokemon.moves.names[i].name == name:", 2)
    script += addScriptLine("currentMove = data.pokemon.moves.stats.battle[i]", 3)
    script += addScriptLine("currentMoveDescription = data.pokemon.moves.descriptions[i - 1]", 3)
    script += addScriptLine("lastIdx = i", 3)
    script += addScriptLine("break", 3)
    script += addScriptLine("")

    # Now update all the move data
    for iid in MAPS.IID_ORDER:
        if iid in MAPS.SKIPPED_IIDS: continue

        # Error handling
        if iid not in adjustedMoves:
            print(f"{iid} not found in adjustedMoves during getMoveScripts. Skipping")
            continue
        if iid not in internalMoves:
            raise Warning(f"{iid} not found in internalMoves during getMoveScripts")
        
        # Grab the adjusted and internal moves generate the script update
        # string to feed to HMA to convert the internalMove into the adjustedMove.
        adjustedMove = adjustedMoves[iid]
        internalMove = internalMoves[iid]
        script += _moveUpdateString(internalMove, adjustedMove)

    script += 'f"Completed Move Update Script with failed moves: {failedMoves}"'
    return [ script ]

def updateCalculatorMoves(adjustedMoves: typing.List[MoveData],):
    
    # Now we need to insert data into the file
    calcFileData = None
    with open("./pokemon-calamity-calc/calc/src/data/moves.ts", "r", encoding="utf_8_sig") as f:
        calcFileData = f.readlines()

    newCalculatorData = []
    # For each pokemon, format the data accordingly
    for iid in MAPS.IID_ORDER:
        if iid in MAPS.SKIPPED_IIDS: continue

        # Error handling
        if iid not in adjustedMoves:
            print(f"{iid} not found in adjustedMoves during updateCalculatorMoves. Skipping")
            continue

        adjustedMove = adjustedMoves[iid]
        newCalculatorData += adjustedMove.getCalcString()

    # Write the species data back into the calc file
    with open("./pokemon-calamity-calc/calc/src/data/moves.ts", "w", encoding="utf_8_sig") as f:

        newData = []

        status = "before"
        for line in calcFileData:
            if status == "before":
                newData.append(line)
                if line == "// BEGIN CUSTOM DATA\n":
                    status = "inside"
                    for l in newCalculatorData:
                        newData.append(l)
            elif status == "inside" and line == "// END CUSTOM DATA\n":
                status = "outside"
                newData.append(line)
            elif status == "outside":
                newData.append(line)

        f.writelines(newData)

if __name__ == "__main__":
    pass

    # Grab the internal moves and adjusted moves
    internalMoves = readInternalMoves()
    adjustedMoves = readMoves()

    # Write the calculator data
    updateCalculatorMoves(adjustedMoves)

    # Get a script that only writes things down for moves that have acutally
    # changes from internal -> adjusted.
    scripts = getMoveScripts(internalMoves, adjustedMoves)
    # writePythonScriptInHMA(scripts)