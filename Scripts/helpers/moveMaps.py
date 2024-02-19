import typing

# Game: The move names as they would appear in the game
# GID: The game name condensed to just the game id
# Calc: The move names as they appear in the calculator. These are
#   also the "standard" or "default" names
# CID: The calc name condensed to just the calc id
# Interal: The raw move name as appears in the following two files
#   ./pokefirered/src/move_descriptions.c
#   ./Complete-Fire-Red-Upgrade/src/Tables/battle_moves.c
# IID: Internal value with all whitespace and nefarious characters removed 

class MAPS:
    _initialized = False

    GID_TO_GAME: typing.Dict[str, str] = {}
    CID_TO_CALC: typing.Dict[str, str] = {}
    IID_TO_INTERNAL: typing.Dict[str, str] = {}

    IGNORED_IIDS: typing.Set[str] = set()
    SKIPPED_IIDS: typing.Set[str] = set()

    CID_TO_IID: typing.Dict[str, str] = {}
    IID_TO_CID: typing.Dict[str, str] = {}

    GAME_TO_CALC: typing.Dict[str, str] = {}
    CALC_TO_GAME: typing.Dict[str, str] = {}
    GAME_TO_INTERNAL: typing.Dict[str, str] = {}
    INTERNAL_TO_GAME: typing.Dict[str, str] = {}
    CALC_TO_INTERNAL: typing.Dict[str, str] = {}
    INTERNAL_TO_CALC: typing.Dict[str, str] = {}

    IID_ORDER: typing.List[str] = []

    def initMoveMaps():
        if not MAPS._initialized:
            _setMaps1()
            _setMaps2()
            _setMaps3()
            MAPS._initialized = True

# List of move ids which we will ignore
IGNORE_MOVES = set(["blank", "nomove", "(nomove)", "movenone", "struggle", "none"])

def toID(name: str) -> str:
    return name.replace(" ", "").replace("'", "").replace("_" ,"").replace("-", "").lower()

# Function for reading ./Complete-Fire-Red-Upgrade/src/Tables/battle_moves.c
# This is responsible for creating the IID_TO_INTERNAL map
def _setMaps1():
    
    # Create moves from the whole battle_moves file first
    with open("./Complete-Fire-Red-Upgrade/src/Tables/battle_moves.c", "r", encoding="utf_8_sig") as f:
        for line in f.readlines():
            if line[:7] == "\t[MOVE_":
                internal = line[7:-4]
                iid = toID(internal)
                MAPS.IID_TO_INTERNAL[iid] = internal

            # Don't worry about any of these moves. They suck
            if line =="#ifdef DYNAMAX_FEATURE\n":
                break

# Function for reading ./Complete-Fire-Red-Upgrade/strings/attack_name_table.string
#   This file has the data needed to create the GID_TO_GAME, GAME_TO_INTERNAL, and INTERNAL_TO_GAME maps
#   It also sets IID_ORDER. This function requires _setMaps1() to have been run prior.
def _setMaps2():
    
    # First, we read in the full name table file
    with open("./Complete-Fire-Red-Upgrade/strings/attack_name_table.string", "r", encoding="utf_8_sig") as f:

        iid, awaitingName = "", False
        start = "#org @NAME_"

        for line in f.readlines():

            # If the line is the start indicator, then we are about to get a description of the name
            if line[:len(start)] == start:
                iid = toID(line[len(start):-1])                
                
                # Ignore all max/gmax moves and specifically ignored moves
                if iid[:3] == "max" or iid[:4] == "gmax":
                    MAPS.IGNORED_IIDS.add(iid)
                    continue
                if iid in IGNORE_MOVES: continue

                # Check to ensure the id is valid
                if iid not in MAPS.IID_TO_INTERNAL:
                    raise Warning(f"{iid} not found in IID_TO_INTERNAL map during _setMaps2().")
                
                awaitingName = True

            elif awaitingName:
                gameName = line[:-1]
                internalName = MAPS.IID_TO_INTERNAL[iid]
                gid = toID(gameName)
                MAPS.GID_TO_GAME[gid] = gameName
                MAPS.GAME_TO_INTERNAL[gameName] = internalName
                MAPS.INTERNAL_TO_GAME[internalName] = gameName
                MAPS.IID_ORDER.append(iid)
                awaitingName = False

# Reads through ./pokemon-calamity-calc/calc/src/data/moves.ts and checks all the names
#   for the calculator moves. This is responsible for creating CID_TO_IID, IID_TO_CID,
#   CID_TO_CALC, CALC_TO_GAME, GAME_TO_CALC, CALC_TO_INTERNAL, and INTERNAL_TO_CALC maps.
def _setMaps3():

    # This is a hand-built map which will correct all the toID() results from the calc
    #   fields to match the correct ID for IID.
    cidToIidCorrections = {
        "drainkiss": "drainingkiss"
    }

    # moves to specifically be ignored by the calculator mappings
    _ignore = set([
        '10,000,000voltthunderbolt', 'aciddownpour', 'alloutpummeling', 'baddybad', 'blackholeeclipse', 'bloomdoom',
        'bouncybubble', 'breakneckblitz', 'buzzybuzz', 'continentalcrush', 'corkscrewcrash', 'devastatingdrake',
        'self', 'freezyfrost', 'gigavolthavoc', 'glitzyglow', 'hydrovortex', 'infernooverdrive', 'let\\ssnuggleforever',
        'neverendingnightmare', 'sappyseed', 'savagespinout', 'shatteredpsyche', 'sizzlyslide', 'sparklyswirl',
        'subzeroslammer', 'supersonicskystrike', 'tectonicrage', 'twinkletackle', 'zippyzap', 'floatyfall', 'pikapapow',
        'splishysplash', 'veeveevolley', 'astralbarrage', 'eeriespell', 'glaciallance', '10,000,000voltthunderbolt',
        'aciddownpour', 'alloutpummeling', 'blackholeeclipse', 'bloomdoom', 'breakneckblitz', 'continentalcrush',
        'corkscrewcrash', 'devastatingdrake', 'gigavolthavoc', 'hydrovortex', 'infernooverdrive', 'let\\ssnuggleforever',
        'neverendingnightmare', 'savagespinout', 'shatteredpsyche', 'subzeroslammer', 'supersonicskystrike', 'tectonicrage',
        'twinkletackle', 'catastropika', 'clangoroussoulblaze', 'extremeevoboost', 'genesissupernova', 'guardianofalola',
        'lightthatburnsthesky', 'maliciousmoonsault', 'menacingmoonrazemaelstrom', 'oceanicoperetta', 'pulverizingpancake',
        'searingsunrazesmash', 'sinisterarrowraid', 'soulstealing7starstrike', 'splinteredstormshards', 'stokedsparksurfer',
        'catastropika', 'clangoroussoulblaze', 'genesissupernova', 'guardianofalola', 'lightthatburnsthesky',
        'maliciousmoonsault', 'menacingmoonrazemaelstrom', 'oceanicoperetta', 'pulverizingpancake', 'searingsunrazesmash',
        'sinisterarrowraid', 'soulstealing7starstrike', 'splinteredstormshards', 'stokedsparksurfer'
    ])

    with open("./pokemon-calamity-calc/calc/src/data/moves.ts", "r", encoding="utf_8_sig") as f:
        for line in f.readlines():
            if ": {" in line and line[0:2] == "  ":
                calcName = line[2:line.index(": {")]
                if calcName[0] == "'" or calcName[0] == '"':
                    calcName = calcName[1:-1]
                cid = toID(calcName)

                if cid in IGNORE_MOVES: continue
                if "hiddenpower" in cid and len(cid) > 11: continue
                if cid in _ignore: continue
                if cid[:3] == "max" or cid [:4] == "gmax": continue
                if "readonly" in cid or "constmap" in cid: continue

                # Handle the straightforward id connections
                MAPS.CID_TO_CALC[cid] = calcName

                # Handle the complicated corrections for total name changes
                iid = cid
                if cid in cidToIidCorrections: iid = cidToIidCorrections[cid]
                MAPS.CID_TO_IID[cid] = iid
                MAPS.IID_TO_CID[iid] = cid

                # Build in all the additional required links
                internalName = MAPS.IID_TO_INTERNAL[iid]
                gameName = MAPS.INTERNAL_TO_GAME[internalName]
                MAPS.CALC_TO_GAME[calcName] = gameName
                MAPS.GAME_TO_CALC[gameName] = calcName
                MAPS.CALC_TO_INTERNAL[calcName] = internalName
                MAPS.INTERNAL_TO_CALC[internalName] = calcName

MAPS.initMoveMaps()

if __name__ == "__main__":
    pass