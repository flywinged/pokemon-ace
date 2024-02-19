from readData import readTypeChart

def writeCalculatorTypeChart():
    typeChart = readTypeChart()
    newCalculatorData = []

    calcFileData = []
    with open("./pokemon-calamity-calc/calc/src/data/types.ts", "r", encoding="utf_8_sig") as f:
        calcFileData = f.readlines()

    for t in typeChart:
        newCalculatorData.append(f"  {t.title()}:" + " {\n")
        for typeInfo in typeChart[t]:
            defenseType, effectiveness = typeInfo
            if effectiveness == "SUPER": effectiveness = "2"
            elif effectiveness == "NOT": effectiveness = "0.5"
            elif effectiveness == "IMMUNE": effectiveness = "0"
            elif effectiveness == "NORMAL": effectiveness = "1"

            newCalculatorData.append(f"    {defenseType.title()}: {effectiveness},\n")
        newCalculatorData.append("  },\n")

    with open("./pokemon-calamity-calc/calc/src/data/types.ts", "w", encoding="utf_8_sig") as f:
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

def writeInternalTypeChart():
    typeChart = readTypeChart()

    FILE_PATH = "./Complete-Fire-Red-Upgrade/src/Tables/type_tables.h"

    fileData = ""
    with open(FILE_PATH, "r", encoding="utf_8_sig") as f:
        fileData = f.read()
    
    for t in typeChart:
        start = f"\t[TYPE_{t.upper()}]=\n" + "\t{\n"
        startIndex = fileData.find(start) + len(start)
        endIndex = startIndex + fileData[startIndex:].find("\t},")
        newData = ""

        effectivenessData = typeChart[t]
        for typeInfo in effectivenessData:
            defenseType, effectiveness = typeInfo
            if effectiveness == "SUPER": effectiveness = "TYPE_MUL_SUPER_EFFECTIVE"
            elif effectiveness == "NOT": effectiveness = "TYPE_MUL_NOT_EFFECTIVE"
            elif effectiveness == "IMMUNE": effectiveness = "TYPE_MUL_NO_EFFECT"
            elif effectiveness == "NORMAL": continue # Skip normal effectiveness
            newData += f"\t\t[TYPE_{defenseType.upper()}] = {effectiveness},\n"

        fileData = fileData[:startIndex] + newData + fileData[endIndex:]
    
    with open(FILE_PATH, "w", encoding="utf_8_sig") as f:
        f.write(fileData)

if __name__ == "__main__":
    writeInternalTypeChart()
    writeCalculatorTypeChart()