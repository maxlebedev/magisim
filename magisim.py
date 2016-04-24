import math
import json
import logging
import sys
import argparse


#in case we want to include the "whole" cardpool
all_sets = ['10E', '9ED', 'BFZ', 'DKA', 'GPT', 'LEA', 'M14', 'OGW', 'RAV', 'THS', 'WWK', '2ED', 'ALA', 'BNG', 'DRK', 'GTC', 'LEB', 'MBS', 'ONS', 'ROE', 'TMP', 'ZEN', '3ED', 'ALL', 'BOK', 'DST', 'HML', 'LEG', 'MIR', 'ORI', 'RTR', 'TOR', '4ED', 'APC', 'CHK', 'DTK', 'ICE', 'LGN', 'MMQ', 'PCY', 'SCG', 'TSP', '5DN', 'ARB', 'CHR', 'EVE', 'INV', 'LRW', 'MOR', 'PLC', 'SHM', 'UDS', '5ED', 'ARN', 'CON', 'EXO', 'ISD', 'M10', 'MRD', 'PLS', 'SOI', 'ULG', '6ED', 'ATH', 'CSP', 'FEM', 'JOU', 'M11', 'NMS', 'PO2', 'SOK', 'USG', '7ED', 'ATQ', 'DGM', 'FRF', 'JUD', 'M12', 'NPH', 'POR', 'SOM', 'VIS', '8ED', 'AVR', 'DIS', 'FUT', 'KTK', 'M13', 'ODY', 'PTK', 'STH', 'WTH']

#loads all cards. Deprecated?
#TODO is there a difference isn the DS depending on how we load?
def load_cards():
	cards = open('/Users/maxlebedev/SWDev/Magisim/AllCards.json').readlines()
	cards = json.loads(cards[0])
	real_cards = dict() #'real' card shave card text, removes vanilla
	for name, card in cards.iteritems():
		if card.get('text'):
			real_cards[name] = card
	return real_cards


#loads a set
def load_set(mtgset):
	cards = open('/Users/maxlebedev/SWDev/magisim/sets/%s.json'%mtgset).readlines()
	cards = json.loads(cards[0])['cards']
	real_cards = dict() #'real' card shave card text, removes vanilla
	for card in cards:
		if card.get('text'):
			logging.debug( 'name:: %s', card['name'])
			real_cards[card['name']] = card
	return real_cards


#TODO care about parts of cards 'sfor' matching 'transform' etc
def similarity_score(word, cards):
	card_tot = len(cards)
	TF = 0 #num card with word
	logging.debug('getting TFIDF for %s'% word)
	for card in cards.keys():
		#logging.debug( cards[card]['text'].lower()
		if word.lower() in cards[card]['text'].lower():
			TF += 1.0
	logging.debug('Term Frequency %d'% TF)
	logging.debug('total %d'% card_tot)
	IDF = math.log(card_tot/TF)
	logging.debug('IDF %f'% IDF)
	TFIDF = TF * IDF
	logging.debug('TFIDF %f'% TFIDF)
	return TFIDF


#find most similar card by total minimum IDF
#TODO implement the rest of cosine similarity
#TODO  num is the number of items to print??
def card_sim(cardname, cards):
	max_sim = 0
	closest_card = 'None'
	for cmpname, cmpcard in cards.iteritems():
		logging.info('processing %s'% cmpname)
		#if cards in common, add TFIDF
		sim = 0#similarity between 2 cards
		for word in cards[cardname]['text'].split():
			if word.lower() in cmpcard['text'].lower():
				sim += similarity_score(word,cards)

		if max_sim < sim and cmpcard['name'] != cardname:
			max_sim = sim
			closest_card = cmpcard['name']
	logging.info('max_sim %f'% max_sim)
	logging.info('closest card %s'% closest_card)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", '--verbose', action="store_true",  help="Verbose output")
	parser.add_argument("-c", '--card',  action="store",  help="Verbose output")
	parser.add_argument("-s", '--sets',  action="store",  help="3 letter codes for sets")
	args = parser.parse_args()
	if args.verbose:
		lvl = logging.DEBUG
	else:
		lvl = logging.INFO
	logging.basicConfig(stream=sys.stderr, level=lvl)
	if args.sets:#if sets are specified, use only those sets
		if args.sets.lower() == 'all':
			sets = all_sets
		else:
			sets = args.sets.split()
		cards = dict()
		for mtgset in sets:
			cards.update(load_set(mtgset))
	else:
		cards = load_cards()

	card_sim(args.card, cards)



