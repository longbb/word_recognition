# coding: utf-8
import os.path, sys
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

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    word_path = module_path + '/result_data/two_syllables_word.pkl'
    word_array = Helper.load_obj(word_path)
    vlsp_word_path = module_path + '/data/bkdictionary.txt'
    vlsp_word_array = Helper.read_new_dictionary(vlsp_word_path)

    new_word = set()
    for word in word_array:
        if word in vlsp_word_array:
            continue
        syllables = word.split('_')
        check_length_syllable = False
        for syllable in syllables:
            if len(syllable) >= 2:
                check_length_syllable = True
                break
        if check_length_syllable:
            new_word.add(word)
    print 'There are %i new word' % len(new_word)

    new_word_text_file = module_path + '/result_data/new_word.txt'
    file = open(new_word_text_file, "w")

    for word in new_word:
        file.write(word + '\n')
    file.close()


    new_word_path = module_path + '/result_data/new_word.pkl'
    Helper.save_obj(word_array, new_word_path)
