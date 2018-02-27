# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
from probabilistic_model import ProbabilisticModel
import csv
import pymongo
from pymongo import MongoClient
import math
import threading
import time

class Model_2(ProbabilisticModel):
    def __init__(self, mbcon, mtcon, mbsup, mtsup, dcon, c):
        super(self.__class__, self).__init__(mbcon, mtcon, mbsup, mtsup, dcon)
        self.c = c

    def confident_model(self, first_syllable, second_syllable):
        bigram = first_syllable + ' ' + second_syllable
        bigram_probability = self.bigram_probability(bigram)['probability']
        if bigram_probability == 0:
            return 0
        first_syllable_probability_info = self.unigram_probability(
            first_syllable
        )
        second_syllable_probability_info = self.unigram_probability(
            second_syllable
        )
        first_syllable_probability = first_syllable_probability_info['probability']
        second_syllable_probability = second_syllable_probability_info['probability']
        first_syllable_occurences = first_syllable_probability_info['number_occurrences']
        second_syllable_occurences = second_syllable_probability_info['number_occurrences']

        first_syllable_phi = self.caculate_phi(first_syllable_occurences)
        second_syllable_phi = self.caculate_phi(second_syllable_occurences)
        first_syllable_probability = math.pow(first_syllable_probability, first_syllable_phi)
        second_syllable_probability = math.pow(second_syllable_probability, second_syllable_phi)

        confident = bigram_probability * bigram_probability
        confident = confident / (first_syllable_probability * second_syllable_probability)
        # import pdb; pdb.set_trace()
        return confident

    def caculate_phi(self, number_occurrences):
        return self.c * math.log10(number_occurrences)

if __name__ == '__main__':
    mbcon = 0.03
    mtcon = 0.03
    mbsup = 100
    mtsup = 100
    probabilistic_model = Model_2(mbcon, mtcon, mbsup, mtsup, 1, 0.36)
    # print probabilistic_model.learning_process()
    # new_sentence = probabilistic_model.word_recognition(u'Việc xét duyệt học bổng cho các năm học sau sẽ dựa vào kết quả học tập và thành tích đóng góp nhiều phong trào tại trường')
    # print new_sentence
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    path_to_csv_file = module_path + '/data/evaluate.csv'
    probabilistic_model.evaluate(path_to_csv_file)
