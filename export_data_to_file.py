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

    two_syllables_path = module_path + '/result_data/two_syllables_word.pkl'
    word_set = Helper.load_obj(two_syllables_path)

    text_file = module_path + '/result_data/text_data.txt'
    file = open(text_file, "w")

    for word in word_set:
        number_syllables = len(word.split('_'))
        if number_syllables == 2:
            file.write(word + '\n')
    file.close()
