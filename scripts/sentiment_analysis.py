import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import csv
from reviews.models import *
import re
import json

import nltk
import sklearn
import numpy as np
import matplotlib.pyplot as plt

from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn

un2wn_mapping = {"VERB" : wn.VERB, "NOUN" : wn.NOUN, "ADJ" : wn.ADJ, "ADV" : wn.ADV}
stopwords = set(nltk.corpus.stopwords.words('english'))
# Pos tags, lemmatizeds a comment accourding to Gianluca's format
def preprocesscomment(raw_comment):
	'''
	raw_comment has to be raw string input
	outputs a list with tokenized, lemmatized, pos_tagged words in 
	the poor Gianluca format: ["word-POS"]

	To add: special lemmatizer for facebook?
	'''
	
	lemmatizer = nltk.WordNetLemmatizer()
	doc = []
	tokenized_comment = nltk.word_tokenize(raw_comment)
	for w, p in nltk.pos_tag(tokenized_comment, tagset="universal"):
            if p in [".", "X"]:  # filtering
                continue
            elif w.lower() in stopwords:
                if w.lower() in ["not", "t", "no"]:  # to handle negation
                    lemma = w.lower()
                    p = "NEGATION"
                else:  # filtering stopwords
                    continue
            elif un2wn_mapping.has_key(p):
                lemma = lemmatizer.lemmatize(w.lower(), pos = un2wn_mapping[p])
            else:
                lemma = lemmatizer.lemmatize(w.lower())
                
            doc.append("-".join([lemma, p]))
	return doc


def sentiwordnetanalysis(doc):
	'''
	lemmatized, post_tagged tokenized list as input in format ["word-POS"] as above.
	returns the polarity score of this doc.
	'''
	polarity = 0
	positive = 0
	negative = 0
	for w in doc:
		if w.split("-")[-1] in ["ADJ", "ADV", "NOUN"]:
			if swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]]) != []:
				positive += swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].pos_score()
				negative += swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].neg_score()
	polarity = positive - negative
	if polarity <= 0:
		print doc
	return polarity





#-----------------------------------------------------------------------------------------------------
#Playing around
with open("filtered_posts_fbid.txt", "rb") as infile:
	question_posts = json.load(infile)

print question_posts

for i in question_posts:
	for j in Post.objects.filter(fb_id = i):
		print sentiwordnetanalysis(preprocesscomment(j.text))


print "bad", sentiwordnetanalysis(["", ""])