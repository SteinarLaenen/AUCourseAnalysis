from __future__ import division
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


def sentiwordnetanalysis1(doc):
	'''
	lemmatized, post_tagged tokenized list as input in format ["word-POS"] as above.
	returns the polarity score of this doc.
	'''
	total_polarity = 0
	positive = 0
	negative = 0
	for w in doc:
		if w.split("-")[-1] in ["ADJ", "ADV", "NOUN"]:
			if swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]]) != []:
				positive += swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].pos_score()
				negative += swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].neg_score()
	total_polarity = positive - negative
	
	if total_polarity >= 0.1:
		return 1
	elif total_polarity <= -0.1:
		return -1
	else:
		return 0

def sentiwordnetanalysis2(doc, obj):
	'''
	doc is lemmatized, post_tagged tokenized list as input in format ["word-POS"] as above.
	returns the polarity score of this doc.

	obj is boundary under which the objectivity score has to be in order for a word to count
	towards the sentiment analysis
	# Seems to be optimal in 0.4-0.6 range
	'''
	total_polarity = 0
	positive = 0
	negative = 0
	for w in doc:
		if w.split("-")[-1] in ["ADJ", "ADV", "NOUN", "VERB"]:
			if swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]]) != []:
				objective = swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].obj_score()
				positive = swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].pos_score()
				negative = swn.senti_synsets(w.split("-")[0], pos = un2wn_mapping[w.split("-")[-1]])[0].neg_score()
				if objective < obj:
					if positive > negative:
						total_polarity += positive
					elif positive < negative:
						total_polarity -= negative
	
	if total_polarity > 0:
		return 1
	else:
		return -1
	

#-----------------------------------------------------------------------------------------------------
#Playing around



correct_list = []

#Find optimal objectivity score

for obj in np.arange(0, 1.1, 0.1):
	test_set_size = 0
	number_correct = 0
	number_positive = 0
	number_negative = 0
	number_neutral = 0
	print "loading:", obj
	for comment in Comment.objects.all():
		if comment.review and (comment.polarity_gs == -1 or comment.polarity_gs == 1):
			comment.polarity_predicted = sentiwordnetanalysis2(preprocesscomment(comment.text), obj)

			if number_negative != 50 and comment.polarity_gs == -1:
				if comment.polarity_predicted == comment.polarity_gs:
					number_correct += 1
	   
				number_negative += 1
				test_set_size += 1
			if number_positive != 50 and comment.polarity_gs == 1:
				if comment.polarity_predicted == comment.polarity_gs:
					number_correct += 1
				
				number_positive += 1
				test_set_size += 1
	correct_list.append(number_correct/82)
			

y = correct_list
x = range(0, 11)
plt.xticks(range(0, 11), [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
#plt.xticks(x, np.arange(0, 1.1, 0.1), size='small');
plt.bar(x, y)
plt.xlabel('Objectivity Threshold')
plt.ylabel('Percentage')
plt.title('Classification Accuracy')
plt.ylim([0.4,1])
plt.show()


print "test set size:", test_set_size, "\n"
print "number of correct classifications:", number_correct, "\n"
print "number of negative posts:", number_negative, "\n"
print "number of positive posts:", number_positive, "\n"
print "number of neutral posts:", number_neutral, "\n"


# for comment in Comment.objects.all():
# 	polarity = sentiwordnetanalysis2(preprocesscomment(comment.text), 0.4)
# 	comment.polarity_predictedr = polarity
	
