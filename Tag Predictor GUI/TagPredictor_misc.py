import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import math
from tqdm import tqdm
import sys
import csv
import time
import pandas as pd
import joblib
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
import dill as pickled
import numpy as np
from scipy.special import softmax

import nltk
nltk.download("punkt")
from nltk.corpus import stopwords
nltk.download("stopwords")
from nltk.stem.wordnet import WordNetLemmatizer
nltk.download('wordnet')
lemma = WordNetLemmatizer()

def qn_scrape(qn_link):
    try:
        qn_page = requests.get(qn_link, allow_redirects=True)
        qn_soup = BeautifulSoup(qn_page.content, 'html.parser')
        qn = qn_soup.find("div", class_="postcell")
        qn_title = qn_soup.find("a", href=qn_link.split('.com')[1])
        qn_body = qn.find("div", class_="s-prose")
        return str(qn_title.text), str(qn_body.text)
    except:
        return "", ""
    
def html_tags_remove(text):
    return BeautifulSoup(text,'lxml').text

def lower_case(text):
    return text.lower()

pattern = r'''(?x)          # set flag to allow verbose regexps
    \w+[+#]+                # ending with pluses or hashes
    | \w+(?:[-.']+\w+)*     # words with optional internal special characters
    | \$?\d+(?:\.\d+)?%?    # currency and percentages, e.g. $12.40, 82%
    '''
    
def tokenizeText(text):
    return nltk.regexp_tokenize(text, pattern)

stop_words = set(stopwords.words("english"))

def filter_stopwords(words):
    filtered_words = []
    for word in words:
        if word not in stop_words:
            filtered_words.append(word)
    return filtered_words
    
def lemmatizeText(words):
    return [lemma.lemmatize(y, pos="v") for y in words]

vectorizer_X1 = joblib.load('../models/vectorizer_x1.joblib')
vectorizer_X2 = joblib.load('../models/vectorizer_x2.joblib')
#vectorizer = joblib.load('../models/Vectorizer.joblib')

def text_splitter(text):
    return text.split()

vec = open("../models/test_vec.pickle", 'rb')
vectorizer = pickled.load(vec)

count_vec = open("../models/test_count_vec.pickle", 'rb')
count_vectorizer = pickled.load(count_vec)

def vectorizeQn(qn):
    X_tfidf = vectorizer.transform(pd.Series([qn]).astype('U'))  
    return X_tfidf

def calcPredScore(y_pred, y_fd):
    temp_list = []
    for i in y_pred:
        temp_list.append(list(i.A[0]))
        
    idx = np.where(np.array(temp_list[0])==1)
    
    a = y_fd[0]
    normalized = (a-min(a))/(max(a)-min(a))
    scores = normalized[idx]
    
    return scores
    
def calcProbScore(y_pred, y_prob):
    temp_list = []
    for i in y_pred:
        temp_list.append(list(i.A[0]))
    idx = np.where(np.array(temp_list[0])==1)
    y_prob = y_fd = np.array(y_prob[0])[idx]
    
    return y_prob