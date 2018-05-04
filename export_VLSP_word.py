# coding: utf-8
import os.path, sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import csv
import pymongo
from pymongo import MongoClient
import math
import threading
from probabilistic_model import ProbabilisticModel
from model2 import Model_2
import multiprocessing
import numpy as np

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    vlsp_folder_path = module_path + '/VLSP_Sentences'
    files = os.listdir(vlsp_folder_path)
    syllables_dictionary = Helper.load_syllables_dictionary()

    sentences = []
    for file in files:
        sentences.extend(Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file))

    word_set = set()
    for sentence in sentences:
        word_array = sentence.split(' ')
        for word in word_array:
            if word in word_set:
                continue
            syllables = word.split('_')
            valid_word = True
            for syllable in syllables:
                if syllable not in syllables_dictionary:
                    valid_word = False
                    continue
            if not valid_word:
                continue
            word_set.add(word)

    dictionary_path = module_path + '/result_data/dictionary.pkl'
    Helper.save_obj(word_set, dictionary_path)
