import typing

_TYPES = [
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice",
    "Fighting", "Poison", "Ground", "Flying", "Psychic",
    "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
]

_EFFECTIVENESS_MAP = {
    "2": "SUPER",
    "1": "NORMAL",
    "0.5": "NOT",
    "0": "IMMUNE"
}

def readTypeChart() -> typing.Dict[str, typing.List[typing.Tuple[str, str]]]:

    typeChart: typing.Dict[str, typing.List[typing.Tuple[str, str]]] = {}

    with open("./data/Types.tsv", "r", encoding="utf_8_sig") as f:
        lines = f.readlines()[1:1+len(_TYPES)]
        for i in range(len(lines)):
            offensiveType = _TYPES[i]
            offensiveEffectiveness: typing.List[typing.Tuple[str, str]] = []
            data = lines[i].split("\t")[1:1+len(_TYPES)]
            for j in range(len(data)):
                defensiveType = _TYPES[j]
                effectiveness = _EFFECTIVENESS_MAP[data[j]]
                offensiveEffectiveness.append((
                    defensiveType,
                    effectiveness
                ))
            typeChart[offensiveType] = offensiveEffectiveness

    return typeChart

if __name__ == "__main__":
    print(readTypeChart())