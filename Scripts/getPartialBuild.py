import os

offset1 = 0
offset2 = 0
with open("./Complete-Fire-Red-Upgrade/offsets.ini", "r") as f:
    lines = f.readlines()
    for line in lines:
        if "gMoveNames:" in line:
            offset1 = line[:-1].replace(" ", "").split(":")[1]
        if "Z_Move_1:" in line:
            offset2 = line[:-1].replace(" ", "").split(":")[1]

offset1int = int(offset1[2:], 16)
offset2int = int(offset2[2:], 16)

dataCut = None
with open("./Complete-Fire-Red-Upgrade/test.gba", "rb") as f:
    data: bytes = f.read()
    dataCut = data[offset1int:offset2int]

rawData = None
with open("./Dynamic-Pokemon-Expansion/test.gba", "rb") as f:
    rawData = f.read()

rawData = rawData[:offset1int] + dataCut + rawData[offset2int:]

location = int("148", 16)
offsetBytes = bytearray.fromhex(offset1[2:])[::-1]
print(offset1, offsetBytes)
offsetBytes += b'\x08'
print(offset1, offset2)
print(offset1int, offset2int)
print(offsetBytes)
rawData = rawData[:location] + offsetBytes + rawData[location+4:]

os.remove("./Complete-Fire-Red-Upgrade/BPRE0.gba")
with open("./Complete-Fire-Red-Upgrade/BPRE0.gba", "wb") as f:
    f.write(rawData)