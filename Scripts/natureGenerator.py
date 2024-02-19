import math
from downloadData import auth, SPREADSHEET_ID

if __name__ == "__main__":

    '''
    Naming convention is as follows:
        Each character represents one of the stats, from a scale of 0-3.
        Based on how they are distributed, 
    '''

    POSITIVE_NATURES = {
        "Attack" : ["Adamant", "Brave", "Lonely", "Naughty"],
        "Defence" : ["Bold", "Impish", "Lax", "Relaxed"],
        "Special Attack": ["Modest", "Mild", "Quiet", "Rash"],
        "Special Defence": ["Calm", "Careful", "Gentle", "Sassy"],
        "Speed": ["Timid", "Hasty", "Jolly", "Naive"]
    }

    NEGATIVE_NATURES = {
        "Attack" : ["Bold", "Modest", "Calm", "Timid"],
        "Defence" : ["Lonely", "Mild", "Gentle", "Hasty"],
        "Special Attack": ["Adamant", "Impish", "Careful", "Jolly"],
        "Special Defence": ["Naughty", "Lax", "Rash", "Naive"],
        "Speed": ["Brave", "Relaxed", "Sassy", "Quiet"]
    }

    TOTAL_EVS = 128
    MAX_PER_STAT = 63

    totalScores = [0, 0, 0, 0, 0, 0]

    data = []
    count = 0
    def determineSpread(attack, defence, specialAttack, specialDefence, speed):
        
        total = attack + defence + specialAttack + specialDefence + speed
        hp = 0
        if total < 19:
            hp = 19 - total
        else:
            hp = (defence + specialDefence) / 2
        if hp < 1:
            hp = 0

        stats = [hp, attack, defence, specialAttack, specialDefence, speed]
        total = sum(stats)
        evsPerPoint = TOTAL_EVS / total

        hpEvs = int(math.floor(hp * evsPerPoint))
        attackEvs = int(math.floor(attack * evsPerPoint))
        defenceEvs = int(math.floor(defence * evsPerPoint))
        specialAttackEvs = int(math.floor(specialAttack * evsPerPoint))
        specialDefenceEvs = int(math.floor(specialDefence * evsPerPoint))
        speedEvs = int(math.floor(speed * evsPerPoint))

        evs = [hpEvs, attackEvs, defenceEvs, specialAttackEvs, specialDefenceEvs, speedEvs]
        while sum(evs) < TOTAL_EVS:
            
            minValue = -1
            minIndex = None
            for i in range(len(evs)):
                if evs[i] and (minIndex is None or evs[i] < minValue):
                    minIndex = i
                    minValue = evs[i]
            
            evs[minIndex] += 1


        average = sum(evs) / 6
        std = 0
        for e in evs:
            std += ((average - e) / 5) ** 2
        std = std**(1/2)

        # Don't include low variance scores
        if std < 6:
            return

        global count
        count += 1

        # Once we have the finalized spread, we want to determine the appropriate nature.
        # attack -> special attack -> speed -> defence -> special defence
        negativeNatures = set()
        if stats[1] == 0:
            negativeNatures = set(NEGATIVE_NATURES["Attack"])
        elif stats[3] == 0:
            negativeNatures = set(NEGATIVE_NATURES["Special Attack"])
        elif stats[5] == 0:
            negativeNatures = set(NEGATIVE_NATURES["Speed"])
        elif stats[2] == 0:
            negativeNatures = set(NEGATIVE_NATURES["Defence"])
        else:
            negativeNatures = set(NEGATIVE_NATURES["Special Defence"])

        # Now we look for the positive natures
        # speed -> attack -> special attack -> defence -> special defense
        positiveNatures = set()
        if stats[1] == 9:
            positiveNatures = set(POSITIVE_NATURES["Attack"])
        elif stats[3] == 9:
            positiveNatures = set(POSITIVE_NATURES["Special Attack"])
        elif stats[5] == 9:
            positiveNatures = set(POSITIVE_NATURES["Speed"])
        elif stats[2] == 9:
            positiveNatures = set(POSITIVE_NATURES["Defence"])
        elif stats[4] == 9:
            positiveNatures = set(POSITIVE_NATURES["Special Defence"])
        
        nature = negativeNatures.intersection(positiveNatures)
        if len(nature) == 0:
            nature = "Serious"
        else:
            nature = list(nature)[0]

        for i in range(6):
            totalScores[i] += evs[i]

        global data
        for i in range(len(stats)):
            stats[i] = str(stats[i])
        data .append(["".join(stats[1:])] + [nature] + [31] + evs) 

    for attack in [0, 1, 4, 9]:
        for defence in [0, 1, 4, 9]:
            for specialAttack in [0, 1, 4, 9]:
                for specialDefence in [0, 1, 4, 9]:
                    for speed in [0, 1, 4, 9]:
                        
                        # Don't process for spreads which everything is the same number
                        stats = [attack, defence, specialAttack, specialDefence, speed]
                        filteredStats = filter(lambda x: x != 0, stats)
                        if len(set(filteredStats)) == 1:
                            continue
                        
                        # Don't include  2+ 1s, 3+ 4s, or 3+ 9s or no 0s
                        if stats.count(1) > 1 or stats.count(4) > 2 or stats.count(9) > 2 or stats.count(0) == 0:
                            continue

                        # If including both attack and special attack, don't include 1/9 pairs
                        if attack and specialAttack:
                            if attack + specialAttack == 10:
                                continue

                        # If including both defence and special defence, don't include 1/9 pairs
                        if defence and specialDefence:
                            if defence + specialDefence == 10:
                                continue
                        
                        # Don't include numbers which total to something quite large or quite small (not possible to distribute)
                        if attack + defence + specialAttack + specialDefence + speed < 10:
                            continue
                        
                        # Don't include this split
                        if attack + defence + specialAttack + specialDefence + speed == 26:
                            continue

                        determineSpread(attack, defence, specialAttack, specialDefence, speed)

    valuesAPI = auth()
    valuesAPI.update(spreadsheetId=SPREADSHEET_ID, range="ivSpreads!A2", body={"values":data}, valueInputOption="RAW").execute()
    print(len(data))