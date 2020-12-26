from functools import reduce
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from bs4 import BeautifulSoup
from multiprocessing.pool import Pool
from multiprocessing import current_process
from functools import partial
from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from sklearn.datasets import make_classification
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import re
import itertools
import time
import csv
import concurrent.futures
import os
import nltk

final_df = pd.read_csv('final_table.csv')
final_df

final_df.groupby('Brand_name')['Brand_name'].nunique().sum()

# Silence the warning
pd.options.mode.chained_assignment = None

new_df = pd.DataFrame(final_df['Name'])

# Categorize by high-level shape
new_df['high-level'] = 0
for i in range(len(new_df)):
    if (re.search(r'\s?shirts?\b', new_df["Name"][i].lower()) != None) and (re.search(r'\s?t-shirts\b', new_df["Name"][i].lower()) == None) \
            or (re.search(r'\s?tops?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?cami?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?polo?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?tank?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?blouse?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?crop?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?tee?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?sleeves?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 1
    elif (re.search(r'\s?hoody?i?e?s?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?jumpers?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?sweaters?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?blazers?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?fleece?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?cardi?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 2
    elif (re.search(r'\s?shorts?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?sk[io]rts?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?trouser?s?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?pants?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?[jl]eggings?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?joggers?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?jeans?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?bottoms?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?sweats?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?culottes?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 3
    elif (re.search(r'\s?dress?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?romper?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?jumpsuit?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?chemise?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?overalls?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?salopettes?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 4
    elif (re.search(r'\s?jackets?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?shackets?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?parka?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?cardigan?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?gilets?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?coat?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?vest?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?trench?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 5
    elif (re.search(r'\s?bra?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?bodysuit?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?body?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?robe?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?briefs?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?underwear?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?thong?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?camisoles?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?tights\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 6
    elif (re.search(r'\s?bikini?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?swimsuit?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?trunks?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 7
    elif (re.search(r'\s?caps?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?hats?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?fedora?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?beanies?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?beret?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 8
    elif (re.search(r'\s?bags?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?backpack?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?purse?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?fanny?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 9
    elif (re.search(r'\s?shoes?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?trainers?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?loafers?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?boots?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?sandals?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?mules?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?sneakers?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?wellies?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?flats?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?slider?s?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?flops?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?pumps?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?espadrilles?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?heels?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?plimsolls?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 10
    elif (re.search(r'\s?belts?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?gloves?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?scarf\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?rings?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?bracelets?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?necklaces?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?glasses\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?braces?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?earringa?s?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?headbands?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?wallet\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?suspenders?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?clutch\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?pendants?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?socks?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?mittens?\b', new_df["Name"][i].lower()) != None):
        new_df['high-level'][i] = 11
        new_df['category'] = 0

for i in range(len(new_df)):
    if (re.search(r'\s?shirts?\b', new_df["Name"][i].lower()) != None) and (re.search(r'\s?t-shirts\b', new_df["Name"][i].lower()) == None) \
            or (re.search(r'\s?tops?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?cami?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?polo?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?tank?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?blouse?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?crop?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?tee?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 1
    elif (re.search(r'\s?jumpers?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?blazers?\b', new_df["Name"][i].lower()) != None)\
            or (re.search(r'\s?sweaters?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?sleeves?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?fleece?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?cardi\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 2
    elif (re.search(r'\s?hoody?i?e?s?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 3
    elif (re.search(r'\s?shorts?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 4
    elif (re.search(r'\s?sk[io]rts?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 5
    elif (re.search(r'\s?trouser?s?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?pants?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?culottes?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 6
    elif (re.search(r'\s?[jl]eggings?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?joggers?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?bottoms?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?sweats?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 7
    elif (re.search(r'\s?jeans?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 8
    elif (re.search(r'\s?dress?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?chemise?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 9
    elif (re.search(r'\s?romper?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?overalls?\b', new_df["Name"][i].lower()) != None)\
            or (re.search(r'\s?jumpsuit?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?salopettes?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 10
    elif (re.search(r'\s?jackets?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?shackets?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?parka?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?cardigan?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?gilets?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?coat?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?vest?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?trench?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 11
    elif (re.search(r'\s?bra?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?bodysuit?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?body?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?robe?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?briefs?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?underwear?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?thong?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?camisoles?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?tights\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 12
    elif (re.search(r'\s?bikini?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?swimsuit?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?trunks?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 13
    elif (re.search(r'\s?caps?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?hats?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?fedora?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?beanies?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?beret?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 14
    elif (re.search(r'\s?bags?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?backpack?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?purse?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?fanny?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 15
    elif (re.search(r'\s?shoes?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?trainers?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?loafers?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?boots?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?sandals?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?mules?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?sneakers?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?wellies?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?flats?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?slider?s?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?flops?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?pumps?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?espadrilles?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?heels?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?plimsolls?\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 16
    elif (re.search(r'\s?belts?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?gloves?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?scarf\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?rings?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?bracelets?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?necklaces?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?glasses\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?braces?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?earringa?s?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?headbands?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?wallet\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?suspenders?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?clutch?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?pendant\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?socks?\b', new_df["Name"][i].lower()) != None) \
            or (re.search(r'\s?mittens?\b', new_df["Name"][i].lower()) != None) or (re.search(r'\s?ear\b', new_df["Name"][i].lower()) != None):
        new_df['category'][i] = 17

# Check for unmarked rows (rows with all 0)
cat = ['high-level', 'category']
test = new_df[reduce(np.logical_and, (new_df[c].values == 0 for c in cat))]
test
