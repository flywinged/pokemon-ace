import typing, csv
from helpers import toID, MAPS, IGNORE_MOVES

class MoveData:

    def __init__(self, data: typing.Dict[str, str], blank = False):
        if blank:
            data = {
                "name": None,
                "effect": None,
                "type": None,
                "power": None,
                "split": None,
                "acc": None,
                "pp": None,
                "se%": None,
                "target": None,
                "priority": None,
                "flags": None,
                "description": None,
            }

        # Used for internal tracking purposes
        self.internalName: str = None
        self.iid: str = None
        self.comments: typing.List[str] = []

        self.name: str = None if data["name"] in [None, ""] else data["name"]
        self.effect: str = None if data["effect"] in [None, ""] else data["effect"]
        self.type: str = None if data["type"] in [None, ""] else data["type"]
        self.power: int = None if data['power'] in [None, ""] else int(data['power'])
        self.split: str = None if data["split"] in [None, ""] else data["split"]
        self.accuracy: int = None if data["acc"] in [None, ""] else int(data["acc"])
        self.pp: int = None if data['pp'] in [None, ""] else int(data['pp'])
        self.effectAccuracy: int = None if data['se%'] in [None, ""] else int(data['se%'])
        self.target: str = None if data['target'] in [None, ""] else data['target']
        self.priority: int = None if data['priority'] in [None, ""] else int(data['priority'])
        self.flags: typing.List[str] = [] if data["flags"] in [None, ""] else data["flags"].split("|")
        self.description: str = None if data["description"] in [None, ""] else data["description"]

    def getCalcString(self) -> typing.List[str]:
        data = [f'\t"{MAPS.GAME_TO_CALC[self.name]}": ' + "{\n"]

        target = ""
        if self.target == "FOES_AND_ALLY": target = "allAdjacent"
        if self.target == "BOTH": target = "allAdjacentFoes"

        multihit = ""
        if self.effect == "DOUBLE_HIT": multihit = "2"
        if self.effect == "MULTI_HIT": multihit = "[2, 5]"
        if self.effect == "TRIPLE_KICK": multihit == "3"
        if self.name == "Dragon Darts": multihit == "2"

        # TODO: Add Recoil Calculations for adjusted moves

        # Write all the data that matters in the calc (namely just base power)
        data += [f"\t\tbp: {self.power},\n"]
        data += [f"\t\ttype: '{self.type}',\n"]
        data += [f"\t\tcategory: '{self.split.title()}',\n"]
        if target != "": data += [f"\t\ttarget: '{target}',\n"]
        if multihit != "": data += [f"\t\tmultihit: {multihit}\n"]

        data += ["\t},\n"]
        return data

def readMoves() -> typing.Dict[str, MoveData]:
    moves = {}
    with open("./data/Moves.tsv", "r", encoding="utf_8_sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            move = MoveData(row)
            if move.name is not None:
                iid = toID(MAPS.GAME_TO_INTERNAL[move.name])
                moves[iid] = move

    return moves

def parseBattleMove(data: typing.List[str]) -> MoveData:
    # Begin with a blank move that we will parse
    blankMove = MoveData({}, True)

    # Grab the moveID from the first line
    blankMove.internalName = data[0][7:-3]
    blankMove.iid = toID(blankMove.internalName)

    # Now grab all the other relevant data in order of appearance
    for info in data[2:]:
        info = info.replace("\n", "").replace(",", "")

        # Track Comments
        if "//" in info:
            info, comment = tuple(info.split("//"))
            blankMove.comments.append(comment)
            MAPS.SKIPPED_IIDS.add(blankMove.iid)

        if " = " not in info: continue
        identifier, arg = tuple(info[3:].split(" = "))

        if identifier == "effect":
            blankMove.effect = arg[7:]
        elif identifier == "power":
            blankMove.power = int(arg)
        elif identifier == "type":
            blankMove.type = arg[5:].title()
        elif identifier == "accuracy":
            blankMove.accuracy = int(arg)
        elif identifier == "pp":
            blankMove.pp = int(arg)
        elif identifier == "secondaryEffectChance":
            blankMove.effectAccuracy = int(arg)
        elif identifier == "target":
            blankMove.target = arg[12:]
        elif identifier == "priority":
            blankMove.priority = int(arg)
        elif identifier == "flags":
            blankMove.flags = arg.replace("FLAG_", "").split(" | ")
        elif identifier == "split":
            blankMove.split = arg[6:]
        
        # We ignore these as z-moves aren't present in the rom hack
        elif identifier == "z_move_power" or identifier == "z_move_effect":
            pass
        else:
            raise Warning(f"Unknown identifier during internal move parse: {identifier}")

    # Ignore moves with 1 pp. Those are special moves I
    # don't give a shit about. Setting the id to None
    # will force it to be ignored
    if blankMove.pp == 1 and blankMove.iid != "sketch":
        blankMove.iid = None

    return blankMove

def parseExistingMoveDescriptions(descriptionMap: typing.Dict[str, typing.List[str]]):

    # Parse the descriptions files and add to the name map
    with open("./pokefirered/src/move_descriptions.c", "r", encoding="utf_8_sig") as f:
        start = "const u8 gMoveDescription_"
        for line in f.readlines():
            line = line[:-4]
            if line[:len(start)] == start:
                iid = line[len(start):line.index("[]")].lower()

                # Edge cases
                if iid == "faintattack": iid = "feintattack"
                if iid == "hijumpkick": iid = "highjumpkick"
                if iid == "smellingsalt": iid = "smellingsalts"
                if iid in IGNORE_MOVES: continue

                description = line[line.index(' = _("')+6:]

                if iid not in descriptionMap:
                    raise Warning(f"Unknown iid in parseExistingMoveDescriptions: {iid}")
                else:
                    descriptionMap[iid].append(description)

def parseNewMoveDescriptions(descriptionMap: typing.Dict[str, typing.List[str]]):
    with open("./Complete-Fire-Red-Upgrade/strings/attack_descriptions.string", "r", encoding="utf_8_sig") as f:

        awaitingDescription = False
        identifier = None
        start = "#org @DESC_"

        for line in f.readlines():
            if line[:len(start)] == start:
                awaitingDescription = True
                identifier = line[len(start):-1]
                identifier = toID(identifier)
                
                # Edge cases
                if identifier in IGNORE_MOVES:
                    awaitingDescription = False

                # Ignore max moves
                if identifier[:3] == "max" or identifier[:4] == "gmax":
                    awaitingDescription = False

            elif awaitingDescription:
                description = line[:-1]
                if identifier not in descriptionMap:
                    raise Warning(f"Unknown identifier in parseNewMoveDescriptions {identifier}")
                else:
                    descriptionMap[identifier].append(description)
                awaitingDescription = False

def getBlankMoveDescriptionMap() -> typing.Dict[str, typing.List[str]]:
    
    # First, we read in the names file
    moveDescriptionMap: typing.Dict[str, typing.List[str]] = {}
    for iid in MAPS.IID_ORDER:
        moveDescriptionMap[iid] = [MAPS.INTERNAL_TO_GAME[MAPS.IID_TO_INTERNAL[iid]]]
    return moveDescriptionMap

def readInternalMoves() -> typing.Dict[str, MoveData]:
    moveDict: typing.Dict[str, MoveData] = {}

    # Create moves from the whole battle_moves file first
    with open("./Complete-Fire-Red-Upgrade/src/Tables/battle_moves.c", "r", encoding="utf_8_sig") as f:

        moveData, gatheringData = [], False
        for line in f.readlines():
            if not gatheringData and line[:7] == "\t[MOVE_":
                moveData.append(line[:-1])
                gatheringData = True
            if gatheringData and line == "\t},\n":
                move = parseBattleMove(moveData)
                moveData = []
                if move.iid is not None and move.iid not in IGNORE_MOVES:
                    moveDict[move.iid] = move
                gatheringData = False
            if gatheringData:
                moveData.append(line)

            # Don't worry about any of these meetings
            if line =="#ifdef DYNAMAX_FEATURE\n":
                break

    # Now we attach existing move names/descriptions
    descriptionMap = getBlankMoveDescriptionMap()
    parseExistingMoveDescriptions(descriptionMap)
    parseNewMoveDescriptions(descriptionMap)

    # Now that we have all the names and descriptions in a nice little bow,
    # We want to attach them to the existing move data
    moves: typing.Dict[str, MoveData] = {}
    for iid in MAPS.IID_ORDER:
        if iid not in moveDict:
            raise Warning(f"Unknown iid in readInternalMoves {iid}")
        else:
            move = moveDict[iid]

            # Don't include commented moves as they probably have issues
            if len(move.comments) > 0:
                continue

            nameData = descriptionMap[iid]
            move.name = nameData[0]
            move.description = nameData[1]
            moves[iid] = move

    return moves

if __name__ == "__main__":
    # moves = readMoves()
    internalMoves = readInternalMoves()

    with open("./test.ssv", "w", encoding="utf_8_sig") as f:
        for moveName in sorted(list(internalMoves)):
            move = internalMoves[moveName]

            f.write(f"{move.name};{move.effect};{move.type};{move.power};{move.split};{move.acc};{move.pp};{move.effectChance};{move.target};{move.priority};{move.description};{'|'.join(move.flags)};{'|'.join(move.comments)}\n")