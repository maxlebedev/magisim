import math
import json
import logging
import sys
import argparse
import re
from tqdm import tqdm
from scipy import spatial

from stemming.porter2 import stem


#ideally we could care about cards legal in formats, but meh

#in case we want to include the "whole" cardpool
legacy = ['10E', '9ED', 'BFZ', 'DKA', 'GPT', 'LEA', 'M14', 'OGW', 'RAV', 'THS', 'WWK', '2ED', 'ALA', 'BNG', 'DRK', 'GTC', 'LEB', 'MBS', 'ONS', 'ROE', 'TMP', 'ZEN', '3ED', 'ALL', 'BOK', 'DST', 'HML', 'LEG', 'MIR', 'ORI', 'RTR', 'TOR', '4ED', 'APC', 'CHK', 'DTK', 'ICE', 'LGN', 'MMQ', 'PCY', 'SCG', 'TSP', '5DN', 'ARB', 'CHR', 'EVE', 'INV', 'LRW', 'MOR', 'PLC', 'SHM', 'UDS', '5ED', 'ARN', 'CON', 'EXO', 'ISD', 'M10', 'MRD', 'PLS', 'SOI', 'ULG', '6ED', 'ATH', 'CSP', 'FEM', 'JOU', 'M11', 'NMS', 'PO2', 'SOK', 'USG', '7ED', 'ATQ', 'DGM', 'FRF', 'JUD', 'M12', 'NPH', 'POR', 'SOM', 'VIS', '8ED', 'AVR', 'DIS', 'FUT', 'KTK', 'M13', 'ODY', 'PTK', 'STH', 'WTH']

modern = ['SOI', 'OGW', 'BFZ', 'ORI', 'DTK', 'FRF', 'KTK', 'M15', 'JOU', 'BNG', 'THS', 'M14', 'DGM', 'GTC', 'RTR', 'M13', 'AVR', 'DKA', 'ISD', 'M12', 'NPH', 'MBS', 'SOM', 'M11', 'ROE', 'WWK', 'ZEN', 'M10', 'ARB', 'CON', 'ALA', 'EVE', 'SHM', 'MOR', 'LRW', '10E', 'FUT', 'PLC', 'TSP', 'CSP', 'DIS', 'GPT', 'RAV', '9ED', 'SOK', 'BOK', 'CHK', '5DN', 'DST', 'MRD', '8ED']


memo = dict()

def get_words(text):
	return re.compile(r'\w+').findall(text)

#loads a set
def load_set(mtgset):
	cards = open('sets/%s.json'%mtgset).readlines()
	cards = json.loads(cards[0])['cards']
	real_cards = dict() #'real' card shave card text, removes vanilla
	for card in cards:
		if card.get('text'):
			logging.debug('name:: %s', card['name'])
			#txt = re.sub(r'\([^)]*\)', '', card['text'])#remove all reminder text
			# I wonder why this messes things up
			card['text'] = stem(card['text'])
			real_cards[card['name']] = card
	return real_cards


def similarity_score(word, cards):
	if word in memo:
		return memo[word]
	card_tot = len(cards)
	TF = 0 #num card with word
	logging.debug('getting TFIDF for %s', word)
	for card in cards.keys():
		if word.lower() in cards[card]['text'].lower():
			TF += 1.0
	IDF = math.log(card_tot/TF)
	TFIDF = TF * IDF
	logging.debug('TF: %d| IDF: %f| TFIDF %f',TF, IDF, TFIDF)
	memo[word] = TFIDF
	return TFIDF


#TODO break up into 2 functions
def card_sim(cardname, cards, howmuch):
	card_text = cards[cardname]['text']
	qwords = set(get_words(card_text)) #words in query card
	card_vec = dict()

	for ind, (cmpname, cmpcard) in enumerate(tqdm(cards.items())):
		if cmpname == cardname:
			continue
		cmp_words = get_words(cmpcard['text'])
		w2 = qwords | set(cmp_words)
		query_vec = dict()
		cmp_vec = dict()

		logging.debug('w2: %s', str(w2))
		logging.debug('cmp_words: %s', str(cmp_words))
		for word in w2:
			query_vec[word] = 0
			cmp_vec[word] = 0
			tfidf = similarity_score(word, cards)
			if word in card_text:
				query_vec[word] = tfidf
			if word in cmpcard['text']:
				cmp_vec[word] = tfidf

		logging.debug('query_vec %s', str(query_vec))
		logging.debug('cmp_vec %s', str(cmp_vec))
		csim = cosine_sim(w2, query_vec, cmp_vec)
		logging.debug('cosine sim: %f', csim)
		card_vec[cmpname] = csim

	#separate function
	for ind, entry in enumerate(sorted(card_vec, key=card_vec.get, reverse=True)):
		if ind > howmuch:
			return
		logging.info('match: %s | score: %f', entry, card_vec[entry])


def cosine_sim(keys, dct1, dct2):
	lst1 = list()
	lst2 = list()
	for k in keys:
		lst1.append(dct1[k])
		lst2.append(dct2[k])
	logging.debug('lst2 %s', str(lst2))
	res = 1 - spatial.distance.cosine(lst1, lst2)
	return res


#main loop
def repl(cards, num_res):
	while True:
		card = raw_input('Please enter a card name:')
		if card == 'exit':
			break
		try:
			card_sim(card, cards, num_res)
		except Keyerror:
			continue


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", '--verbose', action="store_true", help="Verbose output")
	parser.add_argument("-s", '--sets', action="store", help="3 letter codes for sets")
	parser.add_argument("-n", '--num', action="store", help="number of results to show")
	args = parser.parse_args()

	lvl = logging.INFO
	if args.verbose:
		lvl = logging.DEBUG
	logging.basicConfig(stream=sys.stderr, level=lvl)
	if args.sets:#if sets are specified, use only those sets
		if args.sets.lower() == 'legacy' or args.sets.lower() == 'all':
			sets = legacy
		elif args.sets.lower() == 'modern':
			sets = modern
		else:
			sets = args.sets.split()
		cards = dict()
		for mtgset in sets:
			cards.update(load_set(mtgset))
	num_res = 10
	if args.num:
		num_res = int(args.num)
	repl(cards, num_res)
	
#TODO reminder text screws with things. Why?
#TODO refactor all these terrible variable names
#TODO care about parts of cards 'sfor' matching 'transform' etc
#TODO 2 card mode where we get deets on the matching

# This is more correct for longer text. Reach Through Mists and the like don't do well

#about stemming.. it might be worth to see the stemmed output of cards
# do we want ngrams?
