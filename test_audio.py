#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 12:55:56 2019

@author: akashi
"""

from wxpy import *
bot = Bot()
bot = Bot(cache_path=True)


my_friend = bot.friends().search('。')[0]
my_friend.send('test')


#===================================GREET====================================

import re
keywords = {
            'greet': ['hello', 'hi', 'hey'], 
            'goodbye': ['bye', 'farewell'],
            'function':['can you do','function']
           }
# Define a dictionary of patterns
patterns = {}

# Iterate over the keywords dictionary
for intent, keys in keywords.items():        #????
    # Create regular expressions and compile them into pattern objects
    patterns[intent] =re.compile( '|'.join(keys))
    


responses = {'greet': 'Hello you! :)', 
             'default': 'default message', 
             'goodbye': 'goodbye for now',
             'function':'I can do follow jobs:1.obtain real-time price for a certain quote 2.Obtain historical intraday data. 4.fffff'
            }

# Define a function to find the intent of a message
def match_intent(message):
    matched_intent = None
    for intent, pattern in patterns.items():
        # Check if the pattern occurs in the message 
        if pattern.search(message):
            matched_intent = intent
    return matched_intent



def find_name(message):
    name = None
    # Create a pattern for checking if the keywords occur
    name_keyword = re.compile("(name|call)")
    # Create a pattern for finding capitalized words
    name_pattern =re.compile('[A-Z]{1}[a-z]*')
    if name_keyword.search(message):
        # Get the matching words in the string
        name_words = name_pattern.findall(message)
        if len(name_words) > 0:
            # Return the name if the keywords are present
            name = ' '.join(name_words)
    return name

# Define respond()
@bot.register(my_friend, TEXT)
def respond(message):
    # Find the name
    name = find_name(message.text)
    if name is None:
        intent = match_intent(message.text)
    # Fall back to the default response
        key = "default"
        if intent in responses:
            key = intent
            return responses[key]      
    elif name is not None:
        return "Hello, {0}!".format(name)
    else:
        return None
    
#===========================Stocks=======================================

from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config

from iexfinance.stocks import Stock
from datetime import datetime
from iexfinance.stocks import get_historical_intraday
# Create a trainer that uses this config
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('demo-rasa.json')

# Create an interpreter by training the model
interpreter = trainer.train(training_data)



#@register


def solution(message):
    # Extract the entities
    entities = interpreter.parse(message)["entities"]
    # Initialize an empty params dictionary
    params = {}
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])
    print(params)
    return params


def getdata_current(params):
    currentprice=None
    print(params["company"])
    stock1=Stock(params["company"])
    currentprice=stock1.get_price()
    
    return currentprice

def getdata_historical(params):
    
    his_open=None
    his_volume=None

    print(params["year"])
    print(params["month"])
    print(params["day"])
    print(params["company"])



    date = datetime(int(params["year"]),int(params["month"]),int(params["day"]))
    historical_data=get_historical_intraday(params["company"], date)[0]
    his_open=historical_data["open"]
    his_volume=historical_data["volume"]

    his_params={
             'historical_open':'{}'.format(his_open),
             'historical_volume':'{}'.format(his_volume)
             }

    return his_params

#from iexfinance.stocks import Stock
#
#stock1= Stock(params[value])
def send_message(state, message):
    print("USER : {}".format(message))
    new_state, response = respond2(state, message)
    print("BOT : {}".format(response))
    return new_state, response
========================Voice input=============
from pydub import AudioSegment
Import speech_recognition as sp_re
re = sp_re.Recognizer()
from io import BytesIO
def txt_recog(message):
	audio = AudioSegment.from_file(BytesIO(msg.get(file()))
	export = audio.export('audiofile.wav', format="wav")
	AUDIO_FILE = 'audiofile.wav'
	user='empty'
	with sp_re.AudioFile(Audiofile) as source:
		print('start voice input.')
		audio=re.record(source)
	try：
		user=re.recognize_google(audio)
		print("Are you saying "+ user)
	except sp_re.UnknowValueError:
		print("Sorry, I cannot understand you.")
	except sp_re.UnknownValueError:
		print("Please try again or use handwriting input.")
	return user
		
======================State Machine===================

INIT=0 
CURRENT_PRICE=1
OPEN_PRICE=2
HISTORICAL_VOLUME=3
FINISH=4



def respond2(state, message):

    (new_state, response) = policy_rules(state, interpret2(message), message)
    return new_state, response


def policy_rules(state, word, message):
    if state is INIT and word is "current_price":
        new_state=CURRENT_PRICE
        response="Its current price {} . Do you want to know more about it?".format(getdata_current(solution(message)))
    if state is INIT and word is "historical_open":
        new_state=OPEN_PRICE
        response="Its open price was {}. Do you want to know more about it?".format(getdata_historical(solution(message))["historical_open"])
    if state is INIT and word is "historical_volume":
        new_state=HISTORICAL_VOLUME
        response="The volume was {}. Do you want to know more about it?".format(getdata_historical(solution(message))["historical_volume"])
    
    if state is CURRENT_PRICE and word is "historical_open":
        new_state=OPEN_PRICE
        response="Its open price was {}. Do you want to know more about it?".format(getdata_historical(solution(message))["historical_open"])
    if state is CURRENT_PRICE and word is "historical_volume":
        new_state=HISTORICAL_VOLUME
        response="The volume was {}. Do you want to know more about it?".format(getdata_historical(solution(message))["historical_volume"])
    if state is CURRENT_PRICE and word is "initial":
        new_state=INIT
        response="What else do you want to know ?"
    if state is CURRENT_PRICE and word is "finish":
        new_state=FINISH
        response="You are welcome!"
    
    if state is OPEN_PRICE and word is "historical_volume":
        new_state=HISTORICAL_VOLUME
        response="The volume was {}. Do you want to know more about it?".format(getdata_historical(solution(message))["historical_volume"])
    if state is OPEN_PRICE and word is "initial":
        new_state=INIT
        response="What else do you want to know?"
    if state is OPEN_PRICE and word is "current_price":
        new_state=CURRENT_PRICE
        response="Its current price {} . Do you want to know more about it?".format(getdata_current(solution(message)))
    if state is OPEN_PRICE and word is "finish":
        new_state=FINISH
        response="You are welcome!"
    if state is OPEN_PRICE and word is "initial":
        new_state=INIT
        response="What else do you want to know ?"
   
    if state is HISTORICAL_VOLUME and word is "current_price":
        new_state=CURRENT_PRICE
        response="Its current price {} . Do you want to know more about it?".format(getdata_current(solution(message)))
    if state is HISTORICAL_VOLUME and word is "historical_open":
        new_state=OPEN_PRICE
        response="Its open price was {}. Do you want to know more about it?".format(getdata_historical(solution(message))["historical_open"])    
    if state is HISTORICAL_VOLUME and word is "finish":
        new_state=FINISH
        response="You are welcome!"
    if state is HISTORICAL_VOLUME and word is "initial":
        new_state=INIT
        response="What else do you want to know ?"
    if state is INIT and word is "finish":
        new_state=FINISH
        response="You are welcome!"
    if word is None:
        new_state=INIT
        response="Sorry, I don't understand you. Just tell me which company do you want to know."
    return new_state, response


def interpret2(message):
    msg = message.lower()
    if 'current' in msg:
        return 'current_price'
    if 'open' in msg:
        return 'historical_open'
    if 'volume' in msg:
        return 'historical_volume'
    if 'finish' in msg:
        return 'finish'
    if 'no' in msg:
        return 'initial'
    return None

  


@bot.register(my_friend, TEXT)
def send_messages(message):
   
    msg=message.text
    if 'current' in msg:
        state=INIT
        state, response= send_message(state, msg)
        last_state=state
    if 'current' not in msg:
        state, response= send_message(last_state, msg)
        last_state=state
    my_friend.send(response)
# Send the messages

    
    