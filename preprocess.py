# -*- coding: utf-8 -*-
"""
===================================
Analysis Tweet Preprocessor

DEPENDENCIES: cython, numpy, scipy, hdbscan, textblob-de(includes en), langid, faker, pymongo

NOTE: textblob needs language files, download them
	  via $ python -m textblob.download_corpora
===================================
"""

import time
import random
import os
import logging
import numpy as np
import requests
from datetime import datetime
from langid import classify
from pymongo import MongoClient, GEO2D, ASCENDING
from textblob import TextBlob as TextBlobEN
from textblob_de import TextBlobDE

# Sensible logging format
# TODO: proper setup for debug and release mode
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)

# TODO: possibly others? see: http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
ALLOWED_WORD_TOKENS = { 'N', 'J', 'V' }

def connect_to_and_setup_database():
	while True:
		try:
			addr = os.getenv('MONGODB_PORT_27017_TCP_ADDR', 'localhost')
			port = os.getenv('MONGODB_PORT_27017_TCP_PORT', '27017')
			passwd = os.getenv('MONGODB_PASS', 'supertopsecret')
			client = MongoClient('mongodb://analysis:' + passwd + '@' + addr + ':' + port + '/analysis')
			db = client.analysis
			db.tweets.ensure_index([("loc", GEO2D), ("date", ASCENDING)])
			logging.info("Connected to database: mongodb://%s:%s/analysis", addr, port)
			return client, db
		except Exception as error: 
			logging.error(repr(error))
			time.sleep(2) # wait with the retry, database is possibly starting up

# basic tweet class, takes the raw tweet data and already preprocesses for a better internal representation
def preprocess_tweet(data):
	try:
		create_on = datetime.utcfromtimestamp(date.timestamp_ms/1000)
		# detect the language of the tweet or use predefined language
		lang = classify(data.text)[0] if not data.lang else data.lang
		# tokenize the text dependent on the language
		blob = None
		if lang == 'en':
			blob = TextBlobEN(data.text)
		elif lang == 'de':
			blob = TextBlobDE(data.text)
		else: # avoid unknown languages
			raise Exception('Unknown language: ' + data.text)
		# get the polarity of the tweet sentences and summerize them
		# NOTE: TextBlobDE is not as great as the english analyzer and is fairly barebone.
		#	    If the resulting polarity is inaccurate, one possibility to solve this is to
		#		only process english tweets
		polarity = 0
		polarity_count = 0
		for sentence in blob.sentences:
			# ignore unimportant sentiment, because in most cases failed detection or hashtag parts from tweet
			if sentence.sentiment.polarity != 0.0:
				polarity = sentence.sentiment.polarity
				polarity_count += 1
		if polarity_count > 0:
			polarity /= polarity_count
		# extract _important_ words from the word tokens
		words = []
		is_hashtag = False
		for tag in blob.tags:
			word = tag[0]
			kind = tag[1]
			# TODO: special behaviour for hashtag is possibly also necessary for @
			if word[0] == '#': # special case means next word is a hashtag
				is_hashtag = True
			else:
				if is_hashtag: # previous word was a hashtag, so remerge with # and save
					words.append("#" + word)
					is_hashtag = False
				else: # just normal word of the tweet
					# check the word is of an allowed grammatical type
					if kind[0] in ALLOWED_WORD_TOKENS: 
						words.append(word)
		# find out where the tweet came from
		...
		# save twitter metrics
		...
		# create tweet object 
		tweet = { "author": author,
				  "created_on": create_on,
				  "words": words,
				  "loc": [lat, lng],
				  "polarity": polarity }
		return tweet
	except Exception as error: # catch exceptions, usually failed language detection
		logging.warning(repr(error))

if __name__ == '__main__':
	# connect to mongodb
	client, db = connect_to_and_setup_database()

	while True:
		raw_tweets = get_new_tweets()
		processed_tweets = list(map(preprocess_tweet, raw_tweets))
		# insert data into mongo
		result = db.tweets.insert_many(data)
		logging.debug("Inserted ids: %s", result.inserted_ids)





