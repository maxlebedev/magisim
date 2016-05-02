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

#stop_words = ['of', 'the', 'a', 'an', 'it']
stop_words = []


memo = dict()

def get_words(text):
	wlist = re.compile(r'\w+').findall(text)
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
			#txt = re.sub(r'\([^)]*\)', '', card['text'])#remove all reminder text
			# I wonder why this messes things up
			card['text'] = stem(txt)
			real_cards[cardname] = card
	return real_cards


def tfidf_word(word, cards, cardtext):
	if word in memo:
		return memo[word]
	card_tot = len(cards)
	TF = 0 #num card with word
	logging.debug('getting TFIDF for %s', word)

	TF = cardtext.count(word)
	IDF = math.log(card_tot/TF)
	TFIDF = TF * IDF
	logging.debug('TF: %d| IDF: %f| TFIDF %f',TF, IDF, TFIDF)
	memo[word] = TFIDF
	return TFIDF


def comp(cards, all_words, card1, card2):#cards are dicts here
	query_vec = dict()
	cmp_vec = dict()

	logging.debug('all_words: %s', str(all_words))
	for word in all_words:
		query_vec[word] = 0
		cmp_vec[word] = 0
		if word in card1['text']:
			query_vec[word] = tfidf_word(word, cards, card1['text'])
		if word in card2['text']:
			cmp_vec[word] = tfidf_word(word, cards, card2['text'])

	logging.debug('query_vec %s', str(query_vec))
	logging.debug('cmp_vec %s', str(cmp_vec))
	return query_vec, cmp_vec


def compare_two(cards, card1, card2):
	qwords = set(get_words(cards[card1]['text'])) #words in query card
	cmp_words = set(get_words(cards[card2]['text']))
	all_words = qwords | cmp_words
	cd1_vec, cd2_vec = comp(cards, all_words, cards[card1], cards[card2])

	logging.info('card1: %s \n card2: %s', qwords, cmp_words)

	csim = cosine_sim(all_words, cd1_vec, cd2_vec)
	logging.info('cosine similarity: %f\n', csim)
	logging.info('common words:\n')

	for word in qwords:
		if word in cmp_words:
			logging.info(word)
			
	


def get_sim_dict(cardname, cards):
	qwords = set(get_words(cards[cardname]['text'])) #words in query card
	similarity_dict = dict()

	for ind, (cmpname, cmpcard) in enumerate(tqdm(cards.items())):
		if cmpname == cardname:
			continue
		cmp_words = get_words(cmpcard['text'])
		w2 = qwords | set(cmp_words)

		query_vec, cmp_vec = comp(cards, w2, cards[cardname], cards[cmpname])
		csim = cosine_sim(w2, query_vec, cmp_vec)
		logging.debug('cosine sim: %f', csim)
		similarity_dict[cmpname] = csim

	return similarity_dict


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
		if card == 'exit':
			break
		if card[0] == '!':
			c1, c2 = card[1:].split('|')
			compare_two(cards, c1, c2)

		try:
			sim_dict = get_sim_dict(card, cards)
			print_top_n(sim_dict, num_res)
		except KeyError:
			continue


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", '--verbose', action="store_true", help="Verbose output")
	parser.add_argument("-s", '--sets', action="store", help="3 letter codes for sets")
	parser.add_argument("-n", '--num', action="store", help="number of results to show")
	parser.add_argument("-c", '--cmp2', action="store", help="Compare 2 cards mode")
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
	if args.cmp2:
		c1, c2 = args.cmp2.split('|')
		compare_two(sets, c1, c2)
	else:
		repl(cards, num_res)
	
#TODO reminder text screws with things. Why?
#TODO refactor all these terrible variable names
#TODO care about parts of cards 'sfor' matching 'transform' etc
#TODO 2 card mode where we get deets on the matching

# This is more correct for longer text. Reach Through Mists and the like don't do well

# do we want ngrams?
