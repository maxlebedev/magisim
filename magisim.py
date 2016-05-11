import math
import json
import logging
import sys
import argparse
import re
from tqdm import tqdm
from scipy import spatial

from stemming.porter2 import stem

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

#ideally we could care about cards legal in formats, but meh

#in case we want to include the "whole" cardpool
legacy = ['10E', '9ED', 'BFZ', 'DKA', 'GPT', 'LEA', 'M14', 'OGW', 'RAV', 'THS', 'WWK', '2ED', 'ALA', 'BNG', 'DRK', 'GTC', 'LEB', 'MBS', 'ONS', 'ROE', 'TMP', 'ZEN', '3ED', 'ALL', 'BOK', 'DST', 'HML', 'LEG', 'MIR', 'ORI', 'RTR', 'TOR', '4ED', 'APC', 'CHK', 'DTK', 'ICE', 'LGN', 'MMQ', 'PCY', 'SCG', 'TSP', '5DN', 'ARB', 'CHR', 'EVE', 'INV', 'LRW', 'MOR', 'PLC', 'SHM', 'UDS', '5ED', 'ARN', 'CON', 'EXO', 'ISD', 'M10', 'MRD', 'PLS', 'SOI', 'ULG', '6ED', 'ATH', 'CSP', 'FEM', 'JOU', 'M11', 'NMS', 'PO2', 'SOK', 'USG', '7ED', 'ATQ', 'DGM', 'FRF', 'JUD', 'M12', 'NPH', 'POR', 'SOM', 'VIS', '8ED', 'AVR', 'DIS', 'FUT', 'KTK', 'M13', 'ODY', 'PTK', 'STH', 'WTH']

modern = ['SOI', 'OGW', 'BFZ', 'ORI', 'DTK', 'FRF', 'KTK', 'M15', 'JOU', 'BNG', 'THS', 'M14', 'DGM', 'GTC', 'RTR', 'M13', 'AVR', 'DKA', 'ISD', 'M12', 'NPH', 'MBS', 'SOM', 'M11', 'ROE', 'WWK', 'ZEN', 'M10', 'ARB', 'CON', 'ALA', 'EVE', 'SHM', 'MOR', 'LRW', '10E', 'FUT', 'PLC', 'TSP', 'CSP', 'DIS', 'GPT', 'RAV', '9ED', 'SOK', 'BOK', 'CHK', '5DN', 'DST', 'MRD', '8ED']

#stop_words = ['of', 'the', 'a', 'an', 'it']
stop_words = []

memo = dict()

def get_words(text):
	wlist = re.compile(r'\w+').findall(text) #maybe we want to treat all mana costs the same?
	wlist = [value for value in wlist if value not in stop_words]
	return wlist

#loads a set
def load_set(mtgset):
	cards = open('sets/%s.json'%mtgset).readlines()
	cards = json.loads(cards[0])['cards']
	real_cards = dict() #'real' cards have card text, if a card does not have rules text, it is pointless to care about it
	for card in cards:
		if card.get('text'):
			cardname = card['name']
			logging.debug('name:: %s',cardname )
			txt = card['text'].replace(cardname, '~') #replace mentions of the name with ~
			card['text'] = stem(txt)
			real_cards[cardname] = card
	return real_cards


def sklearn(cards, card):
	txtlst = list()
	names = list()
	for i, (c,v) in enumerate(cards.items()):
                if card.lower() == c.lower():
                    card = c
		txtlst.append(v['text'])
		names.append(c)
	crdind = names.index(card)

	tfidf_vectorizer = TfidfVectorizer(token_pattern='\w+')
	tfidf_matrix = tfidf_vectorizer.fit_transform(txtlst)

	csim = cosine_similarity(tfidf_matrix[crdind:crdind+1], tfidf_matrix)[0]

	simdict = dict()
	for i in range(len(names)):
		simdict[names[i]] = csim[i]
	return simdict


def print_top_n(cards, n):
	#separate function
	for ind, entry in enumerate(sorted(cards, key=cards.get, reverse=True)):
		if ind > n:
			return
		logging.info('match: %s | score: %f', entry, cards[entry])


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
                if not card:
                        continue
		if card == 'exit':
			break
		if card[0] == '!':
			c1, c2 = card[1:].split('|')
			compare_two(cards, c1, c2)
                else:
                    try:
                            sim_dict = sklearn(cards, card.strip())
                            print_top_n(sim_dict, num_res)
                    except Exception as e:
                            logging.info(e)
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
	
#TODO long/complicated keywords are weighted too highly
#TODO refactor all these terrible variable names
#TODO 2 card mode where we get deets on the matching. maybe

# do we want ngrams?

