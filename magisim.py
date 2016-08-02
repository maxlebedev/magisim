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


#stop_words = ['of', 'the', 'a', 'an', 'it']
stop_words = []

memo = dict()

# '/Users/maxlebedev/SWDev/DeckBuilder/phrases', '/Users/maxlebedev/SWDev/DeckBuilder/uniq_phras'
def construct_unique_phrase_list(phr_path, output):
    #code snippet that word2vec's phrase tool and collects all the uniques.
    # The goal here is to place these phrases in the cardtext at some point
    inp = open(phr_path, 'r')
    inp = inp.readlines()
    out = open(output, 'w')
    set_phr = set()
    for line in inp:
	words = re.compile(r'[^\s,().]+_[^\s,().]+').findall(line)
	for word in words:
		if word not in set_phr:
			out.write(word+'\n')
			set_phr.update({word})


def get_words(text):
	wlist = re.compile(r'\w+_?\w*').findall(text) #maybe we want to treat all mana costs the same?
	wlist = [value for value in wlist if value not in stop_words]
	return wlist

#loads a set
def load_set():
        cards = open('AllCards.json').readlines()
	cards = json.loads(cards[0])
	real_cards = dict() #'real' cards have card text, if a card does not have rules text, it is pointless to care about it
	for cardname, etc in cards.iteritems():
		if 'text' in etc:
			logging.debug('name:: %s',cardname )
			txt = etc['text'].replace(cardname, '~') #replace mentions of the name with ~
                        etc['text'] = stem(txt)
			real_cards[cardname] = etc
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
	parser.add_argument("-n", '--num', action="store", help="number of results to show")
	args = parser.parse_args()

	lvl = logging.INFO
	if args.verbose:
		lvl = logging.DEBUG
	logging.basicConfig(stream=sys.stderr, level=lvl)
        cards = dict()
        cards.update(load_set()) #mtgset being AllCards
	num_res = 10
	if args.num:
		num_res = int(args.num)
        repl(cards, num_res)
	
#TODO long/complicated keywords are weighted too highly
#TODO refactor all these terrible variable names
#TODO 2 card mode where we get deets on the matching. maybe

# do we want ngrams?

