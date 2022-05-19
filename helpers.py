import os
import requests
import json
from flask import Flask, request, render_template
import PIL
from PIL import Image
from git import Repo, Git

#User-defined config file
import conf

########################## CONF ##########################

DEBUG = conf.datasources["debug"]
DATA_DIR = conf.datasources["data_dir"]
LOCAL_SPRITES_GIT_REPO = conf.git_repo["rootdir"]

########################## MAIN ##########################
#Backend Flask app code starts there
app = Flask(__name__)

def getIFPokemonList():
	document_path = os.getcwd() + '/data/if_pokemons.txt'
	IFPokemonsFile = open(document_path, "r")
	IFPokemonsList = IFPokemonsFile.readlines()
	IFPokemonsFile.close()
	IFPokemonsList = ' '.join(IFPokemonsList).replace('\\n','').split()
	return IFPokemonsList

def getId(name):
	name = name.lower().replace('.', '-').replace('\'', '')
	return name

def getFusionLearnset(headMoves, bodyMoves):
	fusionLearnset = []
	for move in headMoves:
		fusionLearnset.append( move['move']['name'].replace('-', '').lower() )
	for move in bodyMoves:
		fusionLearnset.append( move['move']['name'].replace('-', '').lower() )
	fusionLearnset = list(dict.fromkeys(fusionLearnset))
	return fusionLearnset

def getFusionStats(headStats, bodyStats):
	fusionStats = {}
	fusionStats['hp'] = int(( ( headStats[0]['base_stat'] * 2 ) + ( bodyStats[0]['base_stat'] ) ) / 3)
	fusionStats['spa'] = int(( ( headStats[3]['base_stat'] * 2 ) + ( bodyStats[3]['base_stat'] ) ) / 3)
	fusionStats['spd'] = int(( ( headStats[4]['base_stat'] * 2 ) + ( bodyStats[4]['base_stat'] ) ) / 3)
	fusionStats['atk'] = int(( ( headStats[1]['base_stat'] ) + ( bodyStats[1]['base_stat'] * 2 ) ) / 3)
	fusionStats['def'] = int(( ( headStats[2]['base_stat'] ) + ( bodyStats[2]['base_stat'] * 2 ) ) / 3)
	fusionStats['spe'] = int(( ( headStats[5]['base_stat'] ) + ( bodyStats[5]['base_stat'] * 2 ) ) / 3)
	return fusionStats

def getFusionTypes(headId, bodyId, headTypes, bodyTypes):
	fusionTypes = []
	fusionType0 = None
	fusionType1 = None
	headType0 = None
	headType1 = None
	bodyType0 = None
	bodyType1 = None
	swapTypesExceptions = ["magnemite", "magneton", "magnezone", "dewgong", "omanyte", "omastar", "scizor"]

	headType0 = headTypes[0]['type']['name']
	if len(headTypes) == 2:
		headType1 = headTypes[1]['type']['name']
	else:
		headType1 = None
	
	bodyType0 = bodyTypes[0]['type']['name']
	if len(bodyTypes) == 2:
		bodyType1 = bodyTypes[1]['type']['name']
	else:
		bodyType1 = None

	if headId in swapTypesExceptions:
		headType0,headType1 = headType1,headType0
	if bodyId in swapTypesExceptions:
		bodyType0,bodyType1 = bodyType1,bodyType0

	if headType1 and bodyType1 and headType0 != bodyType0:
		fusionType0 = headType0
		fusionType1 = bodyType0
	elif headType1 is None and bodyType1 is None and headType0 == bodyType0:
		fusionType0 = headType0
		fusionType1 = None
	elif headType1 and bodyType1 is None and headType0 != bodyType0:
		fusionType0 = headType0
		fusionType1 = bodyType0
	elif headType1 and bodyType1 is None and headType0 == bodyType0:
		fusionType0 = headType0
		fusionType1 = headType1
	elif headType1 is None and bodyType1 and headType0 != bodyType1:
		fusionType0 = headType0
		fusionType1 = bodyType1
	elif headType1 is None and bodyType1 and headType0 == bodyType1:
		fusionType0 = headType0
		fusionType1 = bodyType0
	elif headType1 and bodyType1 and headType0 != bodyType1:
		fusionType0 = headType0
		fusionType1 = bodyType1
	elif headType1 and bodyType1 and headType0 == bodyType1:
		fusionType0 = headType0
		fusionType1 = bodyType0
	else:
		fusionType0 = headType0
		fusionType1 = bodyType0

	# Typing IF exceptions
	if headId in ['bulbasaur', 'ivysaur', 'venusaur']:
		fusionType0 = 'Grass'
	if headId in ['charizard', 'moltres']:
		fusionType0 = 'Fire'
	if headId in ['geodude', 'graveler', 'golem', 'onix']:
		fusionType0 = 'Rock'
	if headId in ['gastly', 'haunter', 'gengar']:
		fusionType0 = 'Ghost'
	if headId in ['scyther']:
		fusionType0 = 'Bug'
	if headId in ['gyarados']:
		fusionType0 = 'Water'
	if headId in ['articuno']:
		fusionType0 = 'Ice'
	if headId in ['zapdos']:
		fusionType0 = 'Electric'
	if headId in ['dragonite']:
		fusionType0 = 'Dragon'
	if headId in ['steelix']:
		fusionType0 = 'Steel'

	if bodyId in ['bulbasaur', 'ivysaur', 'venusaur']:
		fusionType1 = 'Grass'
	if bodyId in ['charizard', 'moltres']:
		fusionType1 = 'Fire'
	if bodyId in ['geodude', 'graveler', 'golem', 'onix']:
		fusionType1 = 'Rock'
	if bodyId in ['gastly', 'haunter', 'gengar']:
		fusionType1 = 'Ghost'
	if bodyId in ['scyther']:
		fusionType1 = 'Bug'
	if bodyId in ['gyarados']:
		fusionType1 = 'Water'
	if bodyId in ['articuno']:
		fusionType1 = 'Ice'
	if bodyId in ['zapdos']:
		fusionType1 = 'Electric'
	if bodyId in ['dragonite']:
		fusionType1 = 'Dragon'
	if bodyId in ['steelix']:
		fusionType1 = 'Steel'

	if (headType0 == 'Flying' and headType1 == 'Normal') or (headType1 == 'Flying' and headType0 == 'Normal'):
		fusionType0 = 'Flying'
	if (bodyType0 == 'Flying' and bodyType1 == 'Normal') or (bodyType1 == 'Flying' and bodyType0 == 'Normal'):
		fusionType1 = 'Flying'

	if fusionType0 == fusionType1:
		fusionType1 = None
	if fusionType0:
		fusionType0 = fusionType0.capitalize()
	if fusionType1:
		fusionType1 = fusionType1.capitalize()

	fusionTypes.append(fusionType0)
	if fusionType1:
		fusionTypes.append(fusionType1)

	return fusionTypes

def getFusionAbilities(headAbilities, bodyAbilities):
	fusionAbilities = {}
	fusionAbility0 = None
	fusionAbility1 = None
	fusionAbilityH = None
	headAbility0 = None
	headAbility1 = None
	headAbilityH = None
	bodyAbility0 = None
	bodyAbility1 = None
	bodyAbilityH = None
	try:
		headAbility0 = headAbilities[0]['ability']['name']
	except KeyError:
		headAbility0 = None
	try:
		if len(headAbilities) >= 2:
			headAbility1 = headAbilities[1]['ability']['name']
	except KeyError:
		headAbility1 = None
	try:
		if len(headAbilities) == 3:
			headAbilityH = headAbilities[2]['ability']['name']
	except KeyError:
		headAbilityH = None
	try:
		bodyAbility0 = bodyAbilities[0]['ability']['name']
	except KeyError:
		bodyAbility0 = None
	try:
		if len(bodyAbilities) >= 2:
			bodyAbility1 = bodyAbilities[1]['ability']['name']
	except KeyError:
		bodyAbility1 = None
	try:
		if len(bodyAbilities) == 3:
			bodyAbilityH = bodyAbilities[2]['ability']['name']
	except KeyError:
		bodyAbilityH = None

	if headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and headAbility0 == bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = None
		fusionAbilityH = None
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and headAbility0 != bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = None
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and headAbility0 == bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = headAbility1
		fusionAbilityH= None
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and headAbility0 != bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbility1
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and (headAbility0 == bodyAbility0 or headAbilityH == bodyAbility0):
		fusionAbility0 = headAbility0
		fusionAbility1 = None
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and headAbility0 != bodyAbility0 and headAbilityH != bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH= headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and (headAbility0 == bodyAbility0 or headAbilityH == bodyAbility0):
		fusionAbility0 = headAbility0
		fusionAbility1 = headAbility1
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH is None and headAbility0 != bodyAbility0 and headAbilityH != bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
						
	if headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 == bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = None
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 == bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = None
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 != bodyAbility0 and headAbility0 != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = bodyAbility0
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 == bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbility1
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 == bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbility1
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility1 != bodyAbility0 and headAbility1 != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbility1
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and (headAbility0 == bodyAbility1 or headAbilityH == bodyAbility1):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 != bodyAbility1 and headAbilityH != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and (headAbility0 == bodyAbility1 or headAbilityH == bodyAbility1):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH is None and headAbility0 != bodyAbility1 and headAbilityH != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbilityH
								
	if headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 == bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = None
		fusionAbilityH = bodyAbility0
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 == bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = None
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 != bodyAbility0 and headAbility0 != bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 == bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbility1
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 == bodyAbility0:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbilityH
		fusionAbilityH = headAbility1
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility1 != bodyAbilityH and headAbility0 != bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = headAbility1
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and (headAbility0 == bodyAbilityH or headAbilityH == bodyAbilityH):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 != bodyAbilityH and headAbilityH != bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbilityH
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and (headAbility0 == bodyAbilityH or headAbilityH == bodyAbilityH):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 is None and bodyAbilityH and headAbility0 != bodyAbilityH and headAbilityH != bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbilityH
		fusionAbilityH = headAbilityH

	if headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 == bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = bodyAbility0
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 == bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 != bodyAbility1 and headAbility0 != bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 == bodyAbilityH:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = bodyAbility0
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 == bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 and headAbilityH is None and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 != bodyAbilityH and headAbility0 != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = bodyAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH and (headAbility0 == bodyAbility1 or headAbilityH == bodyAbility1):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 is None and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 != bodyAbility1 and headAbilityH != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH and headAbility0 != bodyAbility1 and headAbilityH != bodyAbility1:
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH and (headAbility0 == bodyAbility1 or headAbilityH == bodyAbility1):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility0
		fusionAbilityH = headAbilityH
	elif headAbility0 and headAbility1 and headAbilityH and bodyAbility0 and bodyAbility1 and bodyAbilityH and (headAbility0 == bodyAbility0 or headAbilityH == bodyAbility0):
		fusionAbility0 = headAbility0
		fusionAbility1 = bodyAbility1
		fusionAbilityH = headAbilityH

	if fusionAbilityH == fusionAbility0 or fusionAbilityH == fusionAbility1:
		fusionAbilityH = None
	if fusionAbility0 == fusionAbility1:
		fusionAbility1 = None
	if fusionAbility0:
		fusionAbility0 = ' '.join([x.capitalize() for x in fusionAbility0.split('-')])
	if fusionAbility1:
		fusionAbility1 = ' '.join([x.capitalize() for x in fusionAbility1.split('-')])
	if fusionAbilityH:
		fusionAbilityH = ' '.join([x.capitalize() for x in fusionAbilityH.split('-')])

	fusionAbilities['0'] = fusionAbility0
	fusionAbilities['1'] = fusionAbility1
	fusionAbilities['H'] = fusionAbilityH

	return fusionAbilities

def getFusionEvolutionaryLine(headId, bodyId):
	headEvos = {'evo1' : '', 'evo2' : ''}
	bodyEvos = {'evo1' : '', 'evo2' : ''}
	evolutionaryLine = {}
	headSpecies = json.loads(requests.get('https://pokeapi.co/api/v2/pokemon-species/' + headId).text)
	bodySpecies = json.loads(requests.get('https://pokeapi.co/api/v2/pokemon-species/' + bodyId).text)
	headEvoChain = json.loads(requests.get(headSpecies['evolution_chain']['url']).text)
	bodyEvoChain = json.loads(requests.get(bodySpecies['evolution_chain']['url']).text)

	headEvos['evo0'] = headEvoChain['chain']['species']['name']
	if len(headEvoChain['chain']['evolves_to']) >= 1:
		headEvos['evo1'] = headEvoChain['chain']['evolves_to'][0]['species']['name']
		if len(headEvoChain['chain']['evolves_to'][0]['evolves_to']) >= 1:
			headEvos['evo2'] = headEvoChain['chain']['evolves_to'][0]['evolves_to'][0]['species']['name']
		else:
			headEvos['evo2'] = ''
	else:
		headEvos['evo1'] = ''
	
	bodyEvos['evo0'] = bodyEvoChain['chain']['species']['name']
	if len(bodyEvoChain['chain']['evolves_to']) >= 1:
		bodyEvos['evo1'] = bodyEvoChain['chain']['evolves_to'][0]['species']['name']
		if len(bodyEvoChain['chain']['evolves_to'][0]['evolves_to']) >= 1:
			bodyEvos['evo2'] = bodyEvoChain['chain']['evolves_to'][0]['evolves_to'][0]['species']['name']
		else:
			bodyEvos['evo2'] = ''
	else:
		bodyEvos['evo1'] = ''

	if headEvos['evo0'] == headId and headEvos['evo1'] != '':
		headEvo = headEvos['evo1'].capitalize()
	elif headEvos['evo1'] == headId and headEvos['evo2'] != '':
		headEvo = headEvos['evo2'].capitalize()
	else:
		headEvo = ''
	if bodyEvos['evo0'] == bodyId and bodyEvos['evo1'] != '':
		bodyEvo = bodyEvos['evo1'].capitalize()
	elif bodyEvos['evo1'] == bodyId and bodyEvos['evo2'] != '':
		bodyEvo = bodyEvos['evo2'].capitalize()
	else:
		bodyEvo = ''
	if headEvo == '' and bodyEvo == '':
		evolutionaryLine['evos'] = None
	elif headEvo == '':
		evolutionaryLine['evos'] = bodyEvo
	elif bodyEvo == '':
		evolutionaryLine['evos'] = headEvo
	else:
		evolutionaryLine['evos'] = headEvo + '-' + bodyEvo
	if headEvos['evo2'] == headId:
		headPrevo = headEvos['evo1'].capitalize()
	elif headEvos['evo1'] == headId:
		headPrevo = headEvos['evo0'].capitalize()
	else:
		headPrevo = ''
	if bodyEvos['evo2'] == bodyId:
		bodyPrevo = bodyEvos['evo1'].capitalize()
	elif bodyEvos['evo1'] == bodyId:
		bodyPrevo = bodyEvos['evo0'].capitalize()
	else:
		bodyPrevo = ''
	if headPrevo == '' and bodyPrevo == '':
		evolutionaryLine['prevo'] = None
	elif headPrevo == '':
		evolutionaryLine['prevo'] = bodyPrevo
	elif bodyPrevo == '':
		evolutionaryLine['prevo'] = headPrevo
	else:
		evolutionaryLine['prevo'] = headPrevo + '-' + bodyPrevo
	return evolutionaryLine

def getFusionData(head, body, pokedexNum, tier):
	headId = getId(head)
	bodyId = getId(body)
	headBaseData = json.loads(requests.get('https://pokeapi.co/api/v2/pokemon/' + headId).text)
	bodyBaseData = json.loads(requests.get('https://pokeapi.co/api/v2/pokemon/' + bodyId).text)
	fusionData = {}
	fusionData['id'] = headId.lower().replace('-', '') + bodyId.lower().replace('-', '')
	fusionData['num'] = pokedexNum
	fusionData['head'] = head
	fusionData['body'] = body
	fusionData['name'] = head + '-' + body
	fusionData['tier'] = tier
	fusionData['types'] = getFusionTypes(headId, bodyId, headBaseData['types'], bodyBaseData['types'])
	fusionData['abilities'] = getFusionAbilities(headBaseData['abilities'], bodyBaseData['abilities'])
	fusionData['learnset'] = getFusionLearnset(headBaseData['moves'], bodyBaseData['moves'])
	fusionData['stats'] = getFusionStats(headBaseData['stats'], bodyBaseData['stats'])
	fusionData['evos'] = getFusionEvolutionaryLine(headId, bodyId)['evos']
	fusionData['prevo'] = getFusionEvolutionaryLine(headId, bodyId)['prevo']
	fusionData['weightkg'] = ( headBaseData['weight'] + bodyBaseData['weight'] ) / 2
	fusionData['heigthm'] = ( headBaseData['height'] + bodyBaseData['height'] ) / 2
	return fusionData

def getPokedexTS(fusionData):
	carriageReturn = "<br/>"
	tabulation = "&nbsp;&nbsp;&nbsp;"
	pokedexTS = ""
	pokedexTS += fusionData['id'] + ': {' + carriageReturn
	pokedexTS += tabulation + 'num: ' + fusionData['num'] + ',' + carriageReturn
	pokedexTS += tabulation + 'name: ' + fusionData['name'] + ',' + carriageReturn
	pokedexTS += tabulation + 'baseSpecies: "' + fusionData['head'] + '",' + carriageReturn
	pokedexTS += tabulation + 'forme: "' + fusionData['body'] + '",' + carriageReturn
	pokedexTS += tabulation + 'types: ' + "[" + ', '.join(map(lambda x: "\"" + x + "\"", fusionData['types'])) + "]" + ',' + carriageReturn
	pokedexTS += tabulation + 'baseStats: {'
	pokedexTS += 'hp: ' + str(fusionData['stats']['hp']) + ', '
	pokedexTS += 'atk: ' + str(fusionData['stats']['atk']) + ', '
	pokedexTS += 'def: ' + str(fusionData['stats']['def']) + ', '
	pokedexTS += 'spa: ' + str(fusionData['stats']['spa']) + ', '
	pokedexTS += 'spd: ' + str(fusionData['stats']['spd']) + ', '
	pokedexTS += 'spe: ' + str(fusionData['stats']['spe'])
	pokedexTS += '},' + carriageReturn
	pokedexTS += tabulation + 'abilities: {'
	if fusionData['abilities']['0']:
		pokedexTS += '0: "' + str(fusionData['abilities']['0']) + '"'
		if fusionData['abilities']['1']:
			pokedexTS += ', 1: "' + str(fusionData['abilities']['1']) + '"'
			if fusionData['abilities']['H']:
				pokedexTS += ', H: "' + str(fusionData['abilities']['H']) + '"'
	elif fusionData['abilities']['H']:
		pokedexTS += 'H: "' + str(fusionData['abilities']['H']) + '"'
	pokedexTS += '},' + carriageReturn
	pokedexTS += tabulation + 'heightm: ' + str(fusionData['heigthm']) + ',' + carriageReturn
	pokedexTS += tabulation + 'weightkg: ' + str(fusionData['weightkg']) + ',' + carriageReturn
	if fusionData['prevo']:
		pokedexTS += tabulation + 'prevo: "' + fusionData['prevo'] + '",' + carriageReturn
		pokedexTS += tabulation + 'evoLevel: 20,' + carriageReturn
	if fusionData['evos']:
		pokedexTS += tabulation + 'evos: ["' + fusionData['evos'] + '"],' + carriageReturn
	pokedexTS += '},'
	return pokedexTS

def getFormatsTS(fusionData):
	carriageReturn = "<br/>"
	tabulation = "&nbsp;&nbsp;&nbsp;"
	formatsTS = ""
	formatsTS += fusionData['id'] + ': {' + carriageReturn
	formatsTS += tabulation + 'tier: ' + fusionData['tier'] + ',' + carriageReturn
	formatsTS += '},'
	return formatsTS

def getLearnsetsTS(fusionData):
	carriageReturn = "<br/>"
	tabulation = "&nbsp;&nbsp;&nbsp;"
	learnsetsTS = ""
	learnsetsTS += fusionData['id'] + ': {' + carriageReturn
	learnsetsTS += tabulation + 'learnset: ' + ': {' + carriageReturn
	for move in fusionData['learnset']:
		learnsetsTS += tabulation + tabulation + move + ": [\"8M\"]," + carriageReturn
	learnsetsTS += tabulation + '},' + carriageReturn
	learnsetsTS += '},'
	return learnsetsTS

# def saveSprite(sprite, type, orientation, filename, autoflip):
# 	filepaths = []
# 	if type == 'regular' and orientation == 'front':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["dex"] + filename)
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5"] + filename)
# 	if type == 'regular' and orientation == 'back' and autoflip == 'no':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back"] + filename)
# 	if type == 'shiny' and orientation == 'front':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["dex-shiny"] + filename)
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-shiny"] + filename)
# 	if type == 'shiny' and orientation == 'back' and autoflip == 'no':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back-shiny"] + filename)
# 	for filepath in filepaths:
# 		tmpSprite = Image.open(sprite)
# 		tmpSprite.save(filepath)
# 	if type == 'regular' and orientation == 'front':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["icons"] + filename)
# 		icon = Image.open(sprite)
# 		icon = icon.resize((40, 40))
# 		icon.save(LOCAL_SPRITES_GIT_REPO + conf.git_repo["icons"] + filename)
# 	if type == 'regular' and orientation == 'back' and autoflip == 'yes':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back"] + filename)
# 		autoflippedBacksprite = Image.open(sprite)
# 		autoflippedBacksprite = autoflippedBacksprite.transpose(PIL.Image.FLIP_LEFT_RIGHT)
# 		autoflippedBacksprite.save(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back"] + filename)
# 	if type == 'shiny' and orientation == 'back' and autoflip == 'yes':
# 		filepaths.append(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back-shiny"] + filename)
# 		autoflippedBacksprite = Image.open(sprite)
# 		autoflippedBacksprite = autoflippedBacksprite.transpose(PIL.Image.FLIP_LEFT_RIGHT)
# 		autoflippedBacksprite.save(LOCAL_SPRITES_GIT_REPO + conf.git_repo["gen5-back-shiny"] + filename)
# 	return filepaths

# def uploadOnGithub(filepaths):
# 	message = "Added: "
# 	os.chdir(LOCAL_SPRITES_GIT_REPO)
# 	repo = Repo.init(LOCAL_SPRITES_GIT_REPO).git
# 	index = Repo.init(LOCAL_SPRITES_GIT_REPO).index
# 	g = Git(LOCAL_SPRITES_GIT_REPO)
# 	g.pull('origin','master')
# 	for filepath in filepaths:
# 		message += "\n" + filepath.split(LOCAL_SPRITES_GIT_REPO)[1]
# 		repo.add(filepath)
# 	index.commit(message)
# 	g.push('origin','master')

########################## ROUTES ##########################

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/getFusionCode',methods = ['POST', 'GET'])
def getFusionCode():
	IFPokemonList = []
	IFPokemonList = getIFPokemonList()
	if request.method == 'POST':
		if request.form:
			head = request.form['headInput']
			body = request.form['bodyInput']
			tier = request.form['tier']
			pokedexNum = request.form['pokedex-num']
			if head not in IFPokemonList or body not in IFPokemonList:
				errorMessage = head+' or '+body+' is not a valid IF Pokémon'
				return render_template('fusionsHelper.html', error=errorMessage, pokemons=IFPokemonList, mimetype='text/html')
			if not pokedexNum.isnumeric():
				errorMessage = pokedexNum+' is not a valid Pokédex number'
				return render_template('fusionsHelper.html', error=errorMessage, pokemons=IFPokemonList, mimetype='text/html')
			fusionData = getFusionData(head, body, pokedexNum, tier)
			print(fusionData)
			pokedexTS = getPokedexTS(fusionData)
			formatsTS = getFormatsTS(fusionData)
			learnsetsTS = getLearnsetsTS(fusionData)
			successMessage = head+'-'+body+' is a valid fusion'
			return render_template('fusionsHelper.html', success=successMessage, pokedexTS=pokedexTS, formatsTS=formatsTS, learnsetsTS=learnsetsTS, pokemons=IFPokemonList, mimetype='text/html')
	return render_template('fusionsHelper.html', pokemons=IFPokemonList)

# @app.route('/addSprites',methods = ['POST', 'GET'])
# def addSprites():
# 	if request.method == 'POST':
# 		if 'sprite' in request.files and request.form:
# 			if '.png' not in request.form['sprite-name']:
# 				return render_template('spritesHelper.html', error='malformed sprite name: missing .png')
# 			filepaths = saveSprite(
# 				request.files['sprite'], 
# 				request.form['sprite-type'], 
# 				request.form['sprite-orientation'], 
# 				request.form['sprite-name'], 
# 				request.form['autoflip']
# 			)
# 			uploadOnGithub(filepaths)
# 			return render_template('spritesHelper.html')
# 	return render_template('spritesHelper.html')

if __name__ == '__main__':
	if DEBUG:
		app.run(debug = DEBUG)
	else:
		app.run(host='0.0.0.0')
