Script Reference: https://github.com/haven1433/HexManiacAdvance/blob/master/src/HexManiac.Core/Models/Code/scriptReference.md

pokefirered
https://github.com/pret/pokefirered/blob/master/INSTALL.md#installation

71C900 - <0A1735>
The following is a guide on how to call event scripts from an item
https://github.com/haven1433/HexManiacAdvance/wiki/Making-Scripts-Callable-from-Items#how-to-run-a-script-from-an-items-use-command-or-from-registering-it-from-select-in-hma

## Items
### EndlessCandy
Var_0x40FF is where the level cap is stored. Run `setvar 0x40FF {cap}` in a overworld script to set the new cap.
Var_0x4034 is for checking if the special items can be used

Var_0x5037 Is the location for the healing map - 0xAABB where AA is the map number and BB is the map bank
Var_0x5038 Is the xLocation of the respawn
Var_0x5039 Is the yLocation of the respawn

PrintWhiteOutRecoveryMessage
EventScript_AfterWhiteOutMomHeal

## Data Extraction for Lua export
```
string = ""
for name in data.pokemon.moves.names:
  string += '\t"' + name.name + '",\n'
string
```

```
string = ""
for name in data.pokemon.names:
  string += '\t"' + name.name + '",\n'
string 
```

```
string = ""
for name in data.items.stats:
  string += '\t"' + name.name + '",\n'
string 
```

```
string = ""
for name in data.pokemon.stats:
  string += f'\t"{name.ability1}","None","None",\n'
string 
```

<!-- Custom Items for PC and Healing -->
section0: # 2D5100
  special HealPlayerParty
  special ShowPokemonStorageSystemPC
  waitstate
  msgbox.default <auto>
{
Leaving PC
}
  closeonkeypress
  end

<!-- Begin Game Items and Things -->
  setvar 0x40FF 11
  additem 68 1
  additem 84 1
  additem 63 1
  additem 74 1
  additem 64 1
  additem 75 1
  additem 65 1
  additem 76 1
  additem 66 1
  additem 77 1
  additem 67 1
  additem 78 1
  additem 70 1
  additem 79 1
  additem 264 1

<!-- Random Starter -->
section0:
  lockall
  random 6
  copyvar 0x4002 0x800D
  if.compare.call 0x4002 0 = <section1>
  if.compare.call 0x4002 1 = <section2>
  if.compare.call 0x4002 2 = <section3>
  if.compare.call 0x4002 3 = <section4>
  if.compare.call 0x4002 4 = <section5>
  if.compare.call 0x4002 5 = <section6>
  msgbox.default <auto>
{
Found [buffer1] inside the pokeball!\n
They seem friendly and join you!
}
  closeonkeypress
  releaseall
  setflag 0x0828
  setflag 0x0024
  addvar 0x402E 1
  hidesprite {insertSprite}
  end

section1:
  givePokemon 1 5 ???????? 0 0 0
  bufferPokemon 0 1
  return

section2:
  givePokemon 152 5 ???????? 0 0 0
  bufferPokemon 0 152
  return

section3:
  givePokemon 277 5 ???????? 0 0 0
  bufferPokemon 0 277
  return

section4:
  givePokemon 440 5 ???????? 0 0 0
  bufferPokemon 0 440
  return

section5:
  givePokemon 548 5 ???????? 0 0 0
  bufferPokemon 0 548
  return

section6:
  givePokemon 758 5 ???????? 0 0 0
  bufferPokemon 0 758
  return