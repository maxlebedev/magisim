import math
import json
import logging
import sys
import argparse
import re
from scipy import spatial


#in case we want to include the "whole" cardpool
legacy = ['10E', '9ED', 'BFZ', 'DKA', 'GPT', 'LEA', 'M14', 'OGW', 'RAV', 'THS', 'WWK', '2ED', 'ALA', 'BNG', 'DRK', 'GTC', 'LEB', 'MBS', 'ONS', 'ROE', 'TMP', 'ZEN', '3ED', 'ALL', 'BOK', 'DST', 'HML', 'LEG', 'MIR', 'ORI', 'RTR', 'TOR', '4ED', 'APC', 'CHK', 'DTK', 'ICE', 'LGN', 'MMQ', 'PCY', 'SCG', 'TSP', '5DN', 'ARB', 'CHR', 'EVE', 'INV', 'LRW', 'MOR', 'PLC', 'SHM', 'UDS', '5ED', 'ARN', 'CON', 'EXO', 'ISD', 'M10', 'MRD', 'PLS', 'SOI', 'ULG', '6ED', 'ATH', 'CSP', 'FEM', 'JOU', 'M11', 'NMS', 'PO2', 'SOK', 'USG', '7ED', 'ATQ', 'DGM', 'FRF', 'JUD', 'M12', 'NPH', 'POR', 'SOM', 'VIS', '8ED', 'AVR', 'DIS', 'FUT', 'KTK', 'M13', 'ODY', 'PTK', 'STH', 'WTH']

modern = ['SOI', 'OGW', 'BFZ', 'ORI', 'DTK', 'FRF', 'KTK', 'M15', 'JOU', 'BNG', 'THS', 'M14', 'DGM', 'GTC', 'RTR', 'M13', 'AVR', 'DKA', 'ISD', 'M12', 'NPH', 'MBS', 'SOM', 'M11', 'ROE', 'WWK', 'ZEN', 'M10', 'ARB', 'CON', 'ALA', 'EVE', 'SHM', 'MOR', 'LRW', '10E', 'FUT', 'PLC', 'TSP', 'CSP', 'DIS', 'GPT', 'RAV', '9ED', 'SOK', 'BOK', 'CHK', '5DN', 'DST', 'MRD', '8ED']


def get_words(text):
    return re.compile('\w+').findall(text)


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
		if word.lower() in cards[card]['text'].lower():
			TF += 1.0
	logging.debug('Term Frequency %d'% TF)
	IDF = math.log(card_tot/TF)
	logging.debug('IDF %f'% IDF)
	TFIDF = TF * IDF
	logging.debug('TFIDF %f'% TFIDF)
	return TFIDF



#TODO better name
#algo only gets 0.4 with itself
#TODO get more than 1 result
def card_sim(cardname, cards):
	card_text = cards[cardname]['text']
	qwords = set(get_words(card_text)) #words in query card

	max_csim = 0.0
	candidate = 'None'
	for ind, (cmpname, cmpcard) in enumerate(cards.iteritems()):
		if cmpname == cardname:
			continue
		cmp_words = get_words(cmpcard['text'])
		w2 = qwords | set(cmp_words)
		query_vec = dict()
		cmp_vec = dict()

		logging.debug('w2: %s' % str(w2))
		logging.debug('cmp_words: %s' % str(cmp_words))
		for word in w2:
			query_vec[word] = 0
			cmp_vec[word] = 0
			tfidf = similarity_score(word,cards) #TODO this bit can be memoized
			if word in card_text:
				query_vec[word] = tfidf
			if word in cmpcard['text']:
				cmp_vec[word] = tfidf
		#now everything is formatted right for cosine similarity
		logging.debug('query_vec %s'% str(query_vec))
		logging.debug('cmp_vec %s'% str(cmp_vec))
		csim = cosine_sim(w2, query_vec, cmp_vec)
		logging.debug('cosine sim: %f' % csim)
		if csim > max_csim:
			max_csim = csim
			candidate = cmpname
	
	logging.info('best match: %s' % candidate)


def cosine_sim(keys, dct1, dct2):
	lst1 = list()
	lst2 = list()
	for k in keys:
		lst1.append(dct1[k])
		lst2.append(dct2[k])
		
	logging.debug('lst2 %s'% str(lst2))
	res = 1 - spatial.distance.cosine(lst1, lst2)
	return res


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
		if args.sets.lower() == 'legacy':
			sets = legacy
		elif args.sets.lower() == 'modern':
			sets = modern
		else:
			sets = args.sets.split()
		cards = dict()
		for mtgset in sets:
			cards.update(load_set(mtgset))

	card_sim(args.card, cards)

#TODO refactor all these terrible variable names

