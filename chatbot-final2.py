import re
from list_of_files import *
import string
import math
# from nltk.corpus import wordnet   #for synonym function
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
import random
from datetime import datetime


import tkinter as tk
from tkinter import *
import ttkbootstrap as tb # to install do: pip install ttkbootstrap
from ttkbootstrap.scrolled import ScrolledText

import time
import os
import sys
import spacy

root = tb.Window(themename="cyborg")
root.title("Simple Virtual Assistant")
root.geometry("690x635")


file_path = 'soccer.txt'

def makelower(input): #turn a string into lowercase
    loweredinput = ''
    for chr in input:
        if chr.isalnum() or chr == ' ':
            loweredinput += chr.lower()
    return loweredinput

def isquestion(input):
    if "?" in input:
        return True
    
    changedinput = makelower(input)
    inputwordlist = changedinput.split(" ")
    if inputwordlist[0] in questionwordlist:
        return True
    changedword = typocheck(inputwordlist[0])
    if changedword in questionwordlist:
        return True
    return False

# removes question mark, period, or exclamation point from sentence
def remove_punctuation(input):
    punctuation_chars = string.punctuation
    # Create a translation table to remove punctuation
    translation_table = str.maketrans("", "", punctuation_chars)
    # Use translate to remove punctuation from the sentence
    cleaned_sentence = input.translate(translation_table)
    return cleaned_sentence

def inputcleanup(input):
    #Taken from laplace soothing project
    #There are many question words in stopwordslist use isquestion to identify if question
    #then use this function to get keywords
    
    cleaninput = makelower(input)
    
    cleaninput = cleaninput.split()
    deletinglist = [] #using a list to avoid messing with the index of the cleaninput for loop

    for word in cleaninput:
        found = False
        for x in stoplist:
            if word == x:
                found = True
        if found == True:
            deletinglist.append(word)
    for y in deletinglist:
        cleaninput.remove(y)
    return cleaninput

# finds the number of times the target word appears in the file 
def occurrences_text(file_path, target_word):
    with open(file_path, 'r') as file:
        #line_count = sum(1 for line in file)
        content = file.read()
        # Using regex to find the number of times the target word appears
        occurrences = len(re.findall(r'\b' + re.escape(target_word) + r'\b', content, re.IGNORECASE))
        return occurrences

# finds the number of lines the document has 
def doc_count(file_path):
    with open(file_path, 'r') as file:
        line_count = sum(1 for line in file)
        return line_count

#finds the number of words in the humaninput
def total_words(input):
    words = input.split()
    total_word_count = len(words)
    return total_word_count

#finds the number of times the target word appears in the humaninput
def word_appearances_input(input, word):
    appearances = input.lower().split().count(word.lower())
    return appearances

# caluclates the tf-idf for each word and puts it and its score in a dictionary
def tf_idf(input):
    input = inputcleanup(input)
    tf_idf_dict = {}
    for item in input:
        total_lines = doc_count(file_path)
        word_total = total_words(humaninput)
        word_input_appearances = word_appearances_input(makelower(humaninput), item)
        word_file_occurrences = occurrences_text(file_path, item)
        tf = word_input_appearances/word_total
        tf_idf = 0
        if word_file_occurrences > 0:
            idf = math.log10(total_lines/word_file_occurrences)
            tf_idf = tf*idf
        else:
            changeditem = typocheck(item)
            if changeditem != None:
                changeditem = inputcleanup(changeditem)
                if changeditem == []:
                    continue #potential to be added into the td idf dict with a value of zero
                changeditem = str(changeditem[0])
                word_file_occurrences = occurrences_text(file_path, changeditem)
                if word_file_occurrences > 0:
                    idf = math.log10(total_lines/word_file_occurrences)
                    tf_idf = tf*idf
                tf_idf_dict[changeditem] = tf_idf
                continue
        tf_idf_dict[item] = tf_idf
    return tf_idf_dict

# sorts the dictionary, removes the keys with values of 0, then appends each remaining key to the keyword list
def get_keyword(tf_idf_dict):
    keywords = []
    sorted_keys = sorted(tf_idf_dict, key=lambda x: tf_idf_dict[x], reverse=True)
    for key, value in tf_idf_dict.items():
        if value > 0:
            keywords.append(key)
    return keywords
    

def keywordtracing(input):
    input = lemmanizedstring(input)
    tf_idf_dict = tf_idf(input)
    keywordlist = get_keyword(tf_idf_dict)
    foundlines = dict()
    for word in keywordlist:
        with open(file_path, 'r') as file:
            content = file.read()
            content = lemmanizedstring(content)
            regexstring = r'(?:[^.!?]*\b' + re.escape(word) + r'\b[^.!?]*[.!?])'
            lineswithword = re.findall(regexstring, content, re.IGNORECASE )
        
        #add all to dictionary after checking all hits with all keywords
        #then use this to find most likely sentence to match question
        
        for x in lineswithword:
            if x in foundlines.keys():
                foundlines[x] = foundlines[x] + 1
            else:
                foundlines[x] = 1
        foundlines = dict(sorted(foundlines.items(), key=lambda item: item[1], reverse=True))
    if len(foundlines) != 0:
        answer = list(foundlines.keys())[0]
        periodCount = findperiodCount(answer,content)
        answer = findOrigionalText(periodCount)
        answerchanged = ''
        answerchanged += repeatQuestion(makelower(humaninput),answer)
        answerchanged += answer
        return answerchanged
    return phrases_when_unsure[random.randint(0,19)]

# def synonyms(input): #probably not useful, but keeping function in case, REMEMBER to uncomment import if using
#     synonyms = []

#     for syn in wordnet.synsets(input):
#         for lm in syn.lemmas():
#                 synonyms.append(lm.name())

#     synonyms.append(input)
#     return (set(synonyms)) #returns a set of synonym for the word

def addToDocument(input):
    with open(file_path, 'a') as file:
        file.write(f"{input}. ")
        return

questiondict = dict()
def repeatQuestion(input,output):
    
    if input in questiondict.keys():
        return repeatquestionlist[random.randint(0,4)] + '\n'
        
    else:
        questiondict[input] = output
    return ''

def lemmanizedstring(input):
    lemmatizer = WordNetLemmatizer()
    content = word_tokenize(input)
    newcontent = ''
    for word in content:
        word = lemmatizer.lemmatize(word)
        newcontent += f'{word} '
    return newcontent #returns completely lemmanized string

def findperiodCount(input,content):
    periodCount = 0
    content = content.split('.')
    for period in content:
        period += '.'
        periodCount += 1
        if period == input:
            break
    return periodCount

def findOrigionalText(input):
    with open(file_path, 'r') as file:
        content = file.read()
        content = content.split('.')
        count = 0
        for sentence in content:
            count += 1
            if count == input:
                answer = sentence
    return answer

def typocheck(input):
    for lists in typodictionary.values():
        for word in lists:
            if word == input:
                return list(typodictionary.keys())[list(typodictionary.values()).index(lists)]
    return None

def identify_name(sentence):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentence)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    # Return None if no name is found
    return None


def loading(chat_window, delay=.25):
    text="..."
    for i in range(3):
        for item in range(len(text)):
            chat_window.insert(tk.END, text[item] + " ")
            chat_window.update()
            time.sleep(delay)
        chat_window.insert(tk.END, '\n')
        chat_window.delete("end-2l", "end-1c")
        chat_window.update()
        time.sleep(delay)


def smooth_transition_gui(chat_window, text, delay=0.046):
    for char in text:
        chat_window.insert(tk.END, char)
        chat_window.update()
        time.sleep(delay)   
    return " "

def polite_check(input):
    message = makelower(input)
    
    msg = ''
    for word in word_tokenize(message):
        typoword = typocheck(word)
        if typoword != None:
            msg += typoword + ' '
            continue
        msg += word + ' '
    
    for item in polite_phrases:
        if item in message or item in msg:
            return True

    return False


def send_message(Event = None):
    global humaninput
    humaninput = GUIinput.get()
    
    if humaninput.strip() != "":
        chat_window.insert(tb.END, "\n")
        chat_window.insert(tb.END, "You: " + humaninput + "\n")
        loading(chat_window)
        isQ = isquestion(humaninput)
        manners = ""
        if isQ == True:
            message = keywordtracing(humaninput)
            politeness = polite_check(humaninput)
            if politeness:
                manners = random.choice(polite_words)
        else:
            addToDocument(humaninput)
            message = random.choice(learning_responses)
        GUIinput.set("")
        chat_window.insert(tb.END, "\n")
        smooth_transition_gui(chat_window,f'Agent: {manners}{message}')
        chat_window.insert(tb.END, "\n")


# Determine the greeting based on the current hour
def time_greeting():    
    # Get the current date and time
    current_time = datetime.now()
    # Extract the current hour
    current_hour = current_time.hour
    # Define the time ranges for greetings
    morning_range = range(6, 12)
    afternoon_range = range(12, 18)
    evening_range = range(18, 24)
    night_range = range(0,6)
    if current_hour in morning_range:
        greeting = "Good morning"
    elif current_hour in afternoon_range:
        greeting = "Good afternoon"
    elif current_hour in evening_range:
        greeting = "Good evening"
    else:
        greeting = "Hello there fellow night owl"
    return greeting


def bot_response(chat_window, response):
    timely_greeting = time_greeting()
    chat_window.insert(tk.END, smooth_transition_gui(chat_window, f'Agent: {timely_greeting},\n{response}'))
    chat_window.insert(tk.END, "\n")

#####   MAIN   #####

chat_window = ScrolledText(root, width=60, height=30, wrap=WORD, autohide=True,
bootstyle="info", font=('Verdana', 15))
chat_window.grid(row=0, column=0, columnspan=2, padx=15, pady=15)
GUIinput = tb.StringVar()

entry_field = tb.Entry(root, textvariable=GUIinput, width= 48, bootstyle="info",
font=('Verdana', 15))
entry_field.grid(row=1, column=0)
entry_field.bind("<Return>",send_message)
send_button = tb.Button(root, text="Send", command=send_message, width=6,
bootstyle="outline")
send_button.grid(row=1, column=1)
topic = 'Juventus Futbol Club'
initial_response = "I am your virtual assistant, ask me anything about Juventus FC (2021 Roster)" 
root.after(500, bot_response(chat_window, initial_response))
root.mainloop()
