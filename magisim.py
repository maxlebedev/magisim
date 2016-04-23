import math
import json
import logging
import sys
import argparse

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
	cards = open('/Users/maxlebedev/SWDev/Magisim/%s.json'%mtgset).readlines()
	cards = json.loads(cards[0])['cards']
	real_cards = dict() #'real' card shave card text, removes vanilla
	for card in cards:
		if card.get('text'):
			logging.debug( 'name:: %s', card['name'])
			real_cards[card['name']] = card
	return real_cards


#TODO care about parts of cards 'sfor' matching 'transform' etc
def similiarity_score(word, cards):
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
		sets = args.sets.split()
		cards = dict()
		for mtgset in sets:
			cards.update(load_set(mtgset))
	else:
		cards = load_cards()

	card_sim(args.card, cards)



