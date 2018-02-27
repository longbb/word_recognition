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
import time
import multiprocessing

rule_01_done = 24360

class ProbabilisticModel(object):
    def __init__(self, mbcon, mtcon, mbsup, mtsup, dcon):
        self.sentence_database = Database('sentence_collection')
        self.bigram_database = Database('bigram_collection')
        self.word_database = Database('word_collection')
        self.mbcon = mbcon
        self.mtcon = mtcon
        self.mbsup = mbsup
        self.mtsup = mtsup
        self.dcon = dcon

    def confident_model(self, first_syllable, second_syllable):
        bigram = first_syllable + ' ' + second_syllable
        bigram_probability = self.bigram_probability(bigram)['probability']
        first_syllable_probability = self.unigram_probability(
            first_syllable
        )['probability']
        second_syllable_probability = self.unigram_probability(
            second_syllable
        )['probability']
        if bigram_probability == 0:
            return 0
        confident = bigram_probability * bigram_probability
        confident = confident / (first_syllable_probability * second_syllable_probability)
        return confident

    def recognition_function(self, first_syllable, second_syllable):
        confident = self.confident_model(first_syllable, second_syllable)
        bigram = first_syllable + ' ' + second_syllable
        occurrences = self.__bigram_occurrences(bigram)
        if confident >= self.mtcon and occurrences >= self.mtsup:
            return 1
        if confident < self.mbcon and occurrences < self.mbsup:
            return -1
        return 0

    def detect_lmc(self, sentence):
        word_array = sentence.split(' ')
        lmc_array = []
        for index, word in enumerate(word_array):
            if index == 0:
                new_lmc = [word_array[0]]
            else:
                first_syllable = word_array[index - 1]
                second_syllable = word
                recognition_value = self.recognition_function(first_syllable, second_syllable)
                if recognition_value == 1:
                    new_lmc.append(word)
                else:
                    lmc_array.append(new_lmc)
                    new_lmc = [word]
        lmc_array.append(new_lmc)
        return lmc_array

    def learning_process(self):
        number_article = self.sentence_database.collection.count()
        print 'Need learing %i article' % number_article
        index_article = 130
        for index in range(index_article, number_article):
            self.article_learning_01(index)


    def article_learning_01(self, index_article):
        print 'Start learning for article % i' % index_article
        find_article_data = self.sentence_database.find_one({
            'article_index': index_article
        })
        if not (find_article_data['success'] and find_article_data['object']):
            print 'Has an exception at %i' % index_article
            return

        article_data = find_article_data['object']
        new_sentence_array = []
        for sentence in article_data['data']:
            self.rule_0_and_1(sentence)
        print 'Learning article %i done' % index_article

    def rule_0_and_1(self, sentence):
        try:
            lmc_array = self.detect_lmc(sentence)

            for lmc_index, lmc in enumerate(lmc_array):
                link_lmc = self.__link_lmc(lmc)
                find_lmc = self.bigram_database.find_one({
                    'key_word': link_lmc
                })
                if not find_lmc['success']:
                    print 'Has an exception at %i' % index
                    return
                if find_lmc['object']:
                    lmc_array[lmc_index] = link_lmc
                elif len(lmc) == 2:
                    lmc_array[lmc_index] = link_lmc
                    # insert new word
                    create_new_word = self.word_database.create({
                        'key_word': link_lmc
                    })
                    create_new_bigram = self.bigram_database.create({
                        'key_word': link_lmc
                    })
        except Exception as error:
            print 'Has an error %s' % str(error)

    def word_recognition(self, sentence):
        lmc_array = self.detect_lmc(sentence)

        for lmc_index, lmc in enumerate(lmc_array):
            link_lmc = self.__link_lmc(lmc)
            find_lmc = self.bigram_database.find_one({
                'key_word': link_lmc
            })
            if not find_lmc['success']:
                print 'Has an exception at %i' % index
                return
            if find_lmc['object']:
                lmc_array[lmc_index] = link_lmc
            elif len(lmc) < 2:
                lmc_array[lmc_index] = link_lmc
            else:
                confident_array = []
                for word_index, word in enumerate(lmc):
                    if word_index > 0:
                        confident_array.append(
                            self.confident_model(lmc[word_index - 1], word)
                        )

                max_confident_index = 0
                max_confident_value = 0
                second_confident_value = 0
                for confident_index, confident in enumerate(confident_array):
                    if confident > max_confident_value:
                        max_confident_index = confident_index
                        second_confident_value = max_confident_value
                        max_confident_value = confident
                different_confident = max_confident_value - second_confident_value
                if different_confident > self.dcon:
                    new_lmc = []
                    word_index = 0
                    while word_index < len(lmc):
                        if word_index == len(lmc) - 1:
                            new_lmc.append(lmc[word_index])
                        else:
                            if word_index == max_confident_index:
                                new_lmc.append(
                                    self.__link_lmc([lmc[word_index], lmc[word_index + 1]])
                                )
                                word_index += 1
                            else:
                                new_lmc.append(lmc[word_index])
                        word_index += 1
                    lmc_array[lmc_index] = ' '.join(new_lmc)
                else:
                    lmc_string = ' '.join(lmc)
                    first_bigram = lmc[0] + ' ' + lmc[1]
                    find_unigram = self.bigram_database.find_one({
                        'key_word': lmc[0]
                    })
                    if find_unigram['object']:
                        bigram_data = find_unigram['object']['data']
                        if first_bigram in bigram_data:
                            array_article = bigram_data[first_bigram]['array_article']
                            number_occurrences = self.__find_number_occurrences(
                                lmc_string, array_article)
                            if number_occurrences > self.mtsup:
                                lmc_array[lmc_index] = link_lmc
                            else:
                                lmc_array[lmc_index] = lmc_string
                        else:
                            lmc_array[lmc_index] = lmc_string
                    else:
                        lmc_array[lmc_index] = lmc_string
        new_sentence = ' '.join(lmc_array)
        return new_sentence


    def unigram_probability(self, unigram):
        find_total_number_occurrences = self.bigram_database.find_one({
            'key_word': 'SYSTEM_CODE|NUMBER_UNIGRAM_OCCURRENCES'
        })
        if not (find_total_number_occurrences['success'] and \
            find_total_number_occurrences['object']):
            return 0
        total_number_occurrences = find_total_number_occurrences['object']['data']

        find_unigram = self.bigram_database.find_one({
            'key_word': unigram
        })
        if not (find_unigram['success'] and find_unigram['object']):
            return 0
        unigram_occurrences = find_unigram['object']['data']['number_occurrences']

        probability = float(unigram_occurrences) / total_number_occurrences
        return {
            'probability': probability,
            'number_occurrences': unigram_occurrences,
            'total_number_occurrences': total_number_occurrences
        }

    def bigram_probability(self, bigram):
        find_total_number_occurrences = self.bigram_database.find_one({
            'key_word': 'SYSTEM_CODE|NUMBER_BIGRAM_OCCURRENCES'
        })
        if not (find_total_number_occurrences['success'] and \
            find_total_number_occurrences['object']):
            return 0
        total_number_occurrences = find_total_number_occurrences['object']['data']
        bigram_occurrences = self.__bigram_occurrences(bigram)
        probability = float(bigram_occurrences) / total_number_occurrences
        return {
            'probability': probability,
            'number_occurrences': bigram_occurrences,
            'total_number_occurrences': total_number_occurrences
        }

    def __bigram_occurrences(self, bigram):
        syllable_array = bigram.split(' ')
        first_syllable = syllable_array[0]

        find_unigram = find_unigram = self.bigram_database.find_one({
            'key_word': first_syllable
        })
        if not (find_unigram['success'] and find_unigram['object']):
            return 0
        bigram_data = find_unigram['object']['data']
        if bigram not in bigram_data:
            return 0
        bigram_occurrences = bigram_data[bigram]['number_occurrences']
        return bigram_occurrences

    def __link_lmc(self, lmc):
        for word in lmc:
            return '_'.join(lmc)

    def __find_number_occurrences(self, lmc_string, array_article):
        number_occurrences = 0
        for article_index in array_article:
            find_article_data = self.sentence_database.find_one({
                'article_index': article_index
            })
            if not (find_article_data['success'] and find_article_data['object']):
                print 'Has an exception at %i' % article_index
                continue

            article_data = find_article_data['object']
            for sentence in article_data['data']:
                number_occurrences += sentence.count(lmc_string)
        return number_occurrences

    def caculate_precesion(self, source_sentence, destination_sentence):
        predict_sentence = self.word_recognition(source_sentence)
        predict_words = predict_sentence.split(' ')
        destination_words = destination_sentence.split(' ')
        number_correct_words = 0
        for predict_word in predict_words:
            if predict_word in destination_words:
                number_correct_words += 1
        return float(number_correct_words) / len(predict_words)

    def evaluate(self, path_to_evaluate_data):
        evaluate_data = Helper.read_file_csv(path_to_evaluate_data)
        max_precesion = 0
        min_precesion = 1
        total_precesion = 0
        array_precesion = []
        for index, data in enumerate(evaluate_data):
            print 'Predict for sentence %i' % index
            precision = self.caculate_precesion(data[0].decode('utf-8'), data[1].decode('utf-8'))
            if precision > max_precesion:
                max_precesion = precision
            if precision < min_precesion:
                min_precesion = precision
            total_precesion += precision
            array_precesion.append(precision)
        average_precesion = total_precesion / len(evaluate_data)
        print 'Max precesion: %f' % max_precesion
        print 'Min precesion: %f' % min_precesion
        print 'Average precesion: %f' % average_precesion
        import pdb; pdb.set_trace()
        return {
            'max_precesion': max_precesion,
            'min_precesion': min_precesion,
            'average_precesion': average_precesion,
            'array_precesion': array_precesion
        }

if __name__ == '__main__':
    mbcon = 0.03
    mtcon = 0.03
    mbsup = 100
    mtsup = 100
    probabilistic_model = ProbabilisticModel(mbcon, mtcon, mbsup, mtsup, 1)
    # print probabilistic_model.learning_process()
    # new_sentence = probabilistic_model.word_recognition(u'Để làm được điều này các nhà nghiên cứu đã cố gắng giảm phần khung bao quanh màn hình làm cho mỏng hơn nhưng vẫn tích hợp nhiều linh kiện hơn kéo theo thời gian nghiên cứu lâu hơn')
    # print new_sentence
    # precision = probabilistic_model.caculate_precesion(source_sentence, destination_sentence)
    # print precision
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    path_to_csv_file = module_path + '/data/evaluate.csv'
    probabilistic_model.evaluate(path_to_csv_file)
