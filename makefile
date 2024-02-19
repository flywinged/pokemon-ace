# Allows easier working directory management in the scripts.
.ONESHELL:

deploy-calc:
	cd pokemon-calamity-calc
	sh ./deploy.sh

build:
	python ./Scripts/build.py setup
	make calculator
	make cfru
	rm -f ./ROMS/*.toml
	python ./Scripts/build.py complete

updatePokemon:
	python ./Scripts/updatePokemon.py

updateTrainers:
	python ./Scripts/updateTrainers.py

base:
	sh ./Scripts/makeBase.sh

calculator:
	cd pokemon-calamity-calc
	node build
	cd ..

calculator-mac:
	cd pokemon-calamity-calc; \
	node build; \
	cd ..

# fire-red runs the pokefirered decomps and creates a base copy of
# pokemon fire red version. It is placed in ROMS/_compiled.gba
# This can only be run on wsl (Windows + R) Type wsl and enter
# As it requires some binaries from linux
fire-red:
	cd pokefirered
	make
	cd ..
	cp './pokefirered/pokefirered.gba' './ROMS/_compiled.gba'

# cfru creates a copy of the hack with DPE and CFRU applied.
# By default, this assumes the copy of the game that the cfru
# is to be applied to is at ./ROMS/_head.gba
cfru:
	cd Dynamic-Pokemon-Expansion
	python scripts/clean.py
	rm -f BPRE0.gba BPRE0.sav test.gba test.sav
	cd ..
	cd Complete-Fire-Red-Upgrade
	python scripts/clean.py
	rm -f BPRE0.gba BPRE0.sav test.gba test.sav
	cd ..

	cp ./ROMS/_head.gba ./Dynamic-Pokemon-Expansion/BPRE0.gba
	cd Dynamic-Pokemon-Expansion
	python scripts/make.py
	cd ..

	cp ./ROMS/_head.gba ./Complete-Fire-Red-Upgrade/BPRE0.gba
	cd Complete-Fire-Red-Upgrade
	python scripts/make.py
	cd ..

	python Scripts/getPartialBuild.py

	cd Complete-Fire-Red-Upgrade
	python scripts/clean.py
	python scripts/make.py
	
	cd ..
	rm ./ROMS/calamity.gba
	cp ./Complete-Fire-Red-Upgrade/test.gba ./ROMS/calamity.gba

# Script to change as needed for testing
test:
	python Scripts/getUpdateEncountersScript.py