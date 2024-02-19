from PIL import Image
from HMA import addScriptLine, writePythonScriptInHMA

# Open the base ROM and make edits to the specific points in memory that are needed
def setItemEffects():
    data: bytes = None
    with open("C:\\Users\\clayt\\Desktop\\pokemon-calamity\\ROMS\\calamity.gba", "rb") as f:
        data = f.read()

    def insertAt(data, idx, ba):
        return data[:idx] + ba + data[idx + len(ba):]

    data = insertAt(data, 2435014, b'\x00\x00\x00\x00\x01\x00\x04\xFF\xFF\xFF')
    data = insertAt(data, 2435024, b'\x00\x00\x00\x00\x02\x00\x04\xFF\xFF\xFF')
    data = insertAt(data, 2435034, b'\x00\x00\x00\x00\x00\x01\x04\xFF\xFF\xFF')
    data = insertAt(data, 2435044, b'\x00\x00\x00\x00\x00\x02\x04\xFF\xFF\xFF')
    data = insertAt(data, 2435054, b'\x00\x00\x00\x00\x00\x08\x04\xFF\xFF\xFF')
    data = insertAt(data, 2435083, b'\x00\x00\x00\x00\x00\x04\x04\xFF\xFF\xFF')

    data = insertAt(data, 2435110, b'\x00\x00\x00\x00\x01\x00\x20\xFF')
    data = insertAt(data, 2435118, b'\x00\x00\x00\x00\x02\x00\x20\xFF')
    data = insertAt(data, 2435126, b'\x00\x00\x00\x00\x00\x01\x20\xFF')
    data = insertAt(data, 2435134, b'\x00\x00\x00\x00\x00\x02\x20\xFF')
    data = insertAt(data, 2435142, b'\x00\x00\x00\x00\x00\x08\x20\xFF')
    data = insertAt(data, 2435150, b'\x00\x00\x00\x00\x00\x04\x20\xFF')

    with open("C:\\Users\\clayt\\Desktop\\pokemon-calamity\\ROMS\\calamity.gba", "wb") as f:
        f.write(data)

NAME_MAP = {
    "HP": "HP",
    "Attack": "Attack",
    "Defense": "Defense",
    "Speed": "Speed",
    "Sp. Atk": "Special Attack",
    "Sp. Def": "Special Defense"
}
def getScriptForVitamin(index: int, name: str, evs: int, refIndex: int = None) -> str:
    script = ""
    script += addScriptLine(f"data.items.stats[{str(index)}].name = '{name}{str(evs)}'")
    script += addScriptLine(f"data.items.stats[{str(index)}].pocket = 'key'")
    script += addScriptLine(f"data.items.stats[{str(index)}]['type'] = 1")
    script += addScriptLine(f"data.items.stats[{str(index)}].description = \"Increases a Pokemon's\\\\n{NAME_MAP[name]} EVs by {str(evs)}.\"")

    if refIndex is not None:
        script += addScriptLine(f"data.items.stats[{index}].fieldeffect = data.items.stats[{refIndex}].fieldeffect")
        script += addScriptLine(f"graphics.items.sprites[{index}].sprite = graphics.items.sprites[{refIndex}].sprite")
        script += addScriptLine(f"graphics.items.sprites[{index}].palette = graphics.items.sprites[{refIndex}].palette")
    
    return script + "\n"

def getItemUpdateScript() -> str:
    script = ""

    # First, adjust the non-vitamin items
    script += addScriptLine("data.items.stats[68].name = 'EndlessCandy'")
    script += addScriptLine("data.items.stats[68].pocket = 'key'")
    script += addScriptLine("data.items.stats[68].fieldeffect = data.items.stats[70].fieldeffect\n")

    script += addScriptLine("data.items.stats[84].name = 'EndlessRepel'")
    script += addScriptLine("data.items.stats[84].pocket = 'key'\n")

    # Then adjust all the 4 and 32 variants of the vitamins
    script += getScriptForVitamin(63, "HP", 4)
    script += getScriptForVitamin(64, "Attack", 4)
    script += getScriptForVitamin(65, "Defense", 4)
    script += getScriptForVitamin(66, "Speed", 4)
    script += getScriptForVitamin(67, "Sp. Atk", 4)
    script += getScriptForVitamin(70, "Sp. Def", 4)

    script += getScriptForVitamin(74, "HP", 32, 63)
    script += getScriptForVitamin(75, "Attack", 32, 64)
    script += getScriptForVitamin(76, "Defense", 32, 65)
    script += getScriptForVitamin(77, "Speed", 32, 66)
    script += getScriptForVitamin(78, "Sp. Atk", 32, 67)
    script += getScriptForVitamin(79, "Sp. Def", 32, 70)

    # Now adjust so all pokemon don't provide EXP or EVS and are always catchable
    # This is so the items we added are actually useful
    script += addScriptLine("for mon in data.pokemon.stats:")
    script += addScriptLine("  mon.catchRate = 255")
    script += addScriptLine("  mon.baseExp = 0")
    script += addScriptLine("  mon.evs.hp = 0")
    script += addScriptLine("  mon.evs.atk = 0")
    script += addScriptLine("  mon.evs['def'] = 0")
    script += addScriptLine("  mon.evs.spd = 0")
    script += addScriptLine("  mon.evs.spatk = 0")
    script += addScriptLine("  mon.evs.spdef = 0")
    script += addScriptLine("  mon.growthrate = 'Slow'")

    script += '"Completed Item Update Script"'
    return [script]

class InsertHeldItemDetails:

    INSERT_AT = 0x900000
    SPRITE_SIZE = 0x100
    PALETTE_SIZE = 0x40

    def __init__(
        self,
        index: int,
        name: str,
        internalName: str,
        description: str,
        filePath: str,
        holdEffect: int = -1,
        param: int = -1,
    ):
        self.index: int = index
        self.name: str = name
        self.internalName: str = internalName
        self.description: str = description
        self.filePath: str = filePath
        self.fileName: str = filePath.split("/")[1]
        self.holdEffect: int = holdEffect
        self.param: int = param
    
    def getScript(self) -> str:

        makeSpriteData = '@!lz(288) ^misc.temp.BPRE_E91CC8`lzs4x3x3` lz 288 20 00 00 17:2 1B 00 00 B0 A1 82 3:7 7A 00 00 A1 88 9:22 FB 00 11 11 1F AA AA CA AA 47 02 DE 3D 67 45 DE DD 3:4 ED 0A 77 56 EE 3E 8:31 0B 3:4 1C 00 0F 00 00 A8 12 00 00 3E 00 28 0F 00 33 A4 01 00 44 00 84 FA 00 00 F0 92 89 00 00 10 9A 99 00 2B 99 99 00 00 AF 88 88 00 AF 77 67 00 00 A1 66 55 00 A1 55 34 00 00 A1 45 E3 78 35 53 43 58 00 28 EB 56 85 02 B0 76 B4 00 00 B0 86 23 00 8B 96 E3 00 BF 68 99 35 53 86 98 5D 00 66 64 87 55 55 1A 00 66 00 66 1A 00 77 77 1A 00 88 02 88 1C 00 99 99 FC 3:4 B2 01 00 99 A9 01 00 99 29 3:113 00 AF 38 DE 00 10 EA DD 00 01 F0 82 DE 00 00 21 8A 3:113 50 C1 3:139 B0 8:152 DD 3E 64 76 08 DD 3E 43 66 3:4 87 D3 3E 00 87 2A AC CC 2C F1 1F 11 40 BF 9:215 98 1A 00 00 A7 B1 1C 00 00 1A 3:193 3:7 17:2\n'
        makePaletteData = '@!lz(32) ^misc.temp.BPRE_E91DEC`lzp4` lz 32 00 D6 5A C6 18 29 31 99 7F 00 56 7F 13 7F F1 7E D5 6A 00 DA 56 DF 42 EF 49 EF 3D 00 8C 3D FF 7F DC 7F 4A 29\n'

        insertScript = ""

        # Setup the sprite and palette pointers
        spriteLoc = InsertHeldItemDetails.INSERT_AT
        insertScript += f"@{hex(InsertHeldItemDetails.INSERT_AT)[2:]}\n"
        insertScript += makeSpriteData
        InsertHeldItemDetails.INSERT_AT += InsertHeldItemDetails.SPRITE_SIZE

        paletteLoc = InsertHeldItemDetails.INSERT_AT
        insertScript += f"@{hex(InsertHeldItemDetails.INSERT_AT)[2:]}\n"
        insertScript += makePaletteData
        InsertHeldItemDetails.INSERT_AT += InsertHeldItemDetails.PALETTE_SIZE

        # Import the image after repointing
        insertScript += f"@graphics.items.sprites/{str(self.index)}/sprite <{hex(spriteLoc)[2:]}>\n"
        insertScript += f"@graphics.items.sprites/{str(self.index)}/palette <{hex(paletteLoc)[2:]}>\n"
        self.resizeImage()
        insertScript += f"@graphics.items.sprites/{str(self.index)}\n"
        insertScript += f"@!importimage(../icons/{self.fileName} smart)\n"

        # Update name anddescriptions accordingly
        insertScript += f"@data.items.stats/{str(self.index)}/name {self.name}\n"
        insertScript += f"@data.items.stats/{str(self.index)}/description @" + '{ "' + self.description + '" @}\n'
        insertScript += f'@data.items.stats/{str(self.index)}/pocket "item"\n'
        insertScript += f'@data.items.stats/{str(self.index)}/type 4\n'
        insertScript += f'@data.items.stats/{str(self.index)}/fieldeffect <null>\n'
        insertScript += f'@data.items.stats/{str(self.index)}/battleeffect <null>\n'
        if self.holdEffect != -1:
            insertScript += f"@data.items.stats/{str(self.index)}/hold {str(self.holdEffect)}\n"
        if self.param != -1:
            insertScript += f"@data.items.stats/{str(self.index)}/param {str(self.param)}\n"

        return insertScript + "\n"

    def resizeImage(self):

        im = Image.open("./pokesprite/items/" + self.filePath)
        resized = im.resize((24, 24))
        resized.save('icons/' + self.fileName)
    
    def updateInternalFiles(self):

        for fileName in [
            "./Dynamic-Pokemon-Expansion/include/items.h",
            "Complete-Fire-Red-Upgrade/include/constants/items.h"
        ]:
            data = None
            with open(fileName, "r") as f:
                data = f.read()
            
            startString = f"#define {self.internalName} "
            startIndex = data.index(startString) + len(startString)
            endIndex = startIndex + data[startIndex:].index("\n")
            data = data[:startIndex] + str(self.index) + data[endIndex:]

            with open(fileName, "w") as f:
                f.write(data)

def insertNewItems():
    NEW_ITEMS = [
        # 1-4 -> Reserved for Pokeballs
        InsertHeldItemDetails(
            5,
            "Black Sludge",
            "ITEM_BLACK_SLUDGE",
            "A hold item that\\ngradually restores the\\nHP of Poison-type Pokemon.\\nIt inflicts damage on\\nall other types.",
            "hold-item/black-sludge.png",
            77
        ),
        InsertHeldItemDetails(
            6,
            "Rocky Helmet",
            "ITEM_ROCKY_HELMET",
            "If the holder of this\\nitem takes damage,\\nthe attacker will also\\nbe damaged upon contact.",
            "hold-item/rocky-helmet.png",
            68
        ),
        InsertHeldItemDetails(
            7,
            "Focus Sash",
            "ITEM_FOCUS_SASH",
            "An item to be held by a Pokemon.\\nIf it has full HP,\\nthe holder will endure one potential KO attack,\\nleaving 1 HP.",
            "hold-item/focus-sash.png",
            39,
        )
    ]

    script = ""
    for item in NEW_ITEMS:
        script += item.getScript()
        item.updateInternalFiles()
    with open("./Scripts/HMA/scripts/addItems.hma", "w") as f:
        f.write(script)

if __name__ == "__main__":
    # setItemEffects()
    # scripts = getItemUpdateScript()
    # writePythonScriptInHMA(scripts)

    # im = Image.open("./pokesprite/items/hold-item/black-sludge.png")
    # resized = im.resize((24, 24))
    # resized.save('icons/black-sludge.png')

    insertNewItems()