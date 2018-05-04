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
import multiprocessing

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'

    two_syllables_path = module_path + '/result_data/two_syllables_word_model2.pkl'
    word_set = Helper.load_obj(two_syllables_path)
    one_syllable_word = []
    two_syllables_word = []
    three_syllables_word = []
    four_syllables_word = []
    other = []
    for word in word_set:
        number_syllables = len(word.split('_'))
        if number_syllables == 2:
            two_syllables_word.append(word)
        elif number_syllables == 1:
            one_syllable_word.append(word)
        elif number_syllables == 3:
            three_syllables_word.append(word)
        elif number_syllables == 4:
            four_syllables_word.append(word)
        else:
            other.append(word)

    print 'There are %i words have one syllable' % len(one_syllable_word)
    print 'There are %i words have two syllables' % len(two_syllables_word)
    print 'There are %i words have three syllables' % len(three_syllables_word)
    print 'There are %i words have four syllables' % len(four_syllables_word)
    print 'There are %i other words' % len(other)
    # import pdb; pdb.set_trace()
