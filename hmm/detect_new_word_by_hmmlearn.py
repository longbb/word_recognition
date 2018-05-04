# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import math
import hmmlearn.hmm as hmm
import numpy as np
from sklearn.externals import joblib

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmmlearn.pkl'
    model = joblib.load(hmm_save_path)

    hmm_learn_dictionary_path = module_path + '/hmm/hmm_data/hmm_learn_dictionary.pkl'
    hmm_dictionary = Helper.load_obj(hmm_learn_dictionary_path)
    import pdb; pdb.set_trace()

    syllables_dictionary = Helper.load_syllables_dictionary()

    vlsp_word_path = module_path + '/data/bkdictionary.txt'
    vlsp_word_array = Helper.read_new_dictionary(vlsp_word_path)

    # array_data_file = {
    #     'AA': 100,
    #     'AB': 100,
    #     'AC': 100,
    #     'AD': 100,
    #     'AE': 100,
    #     'AF': 100,
    #     'AG': 100,
    #     'AH': 82
    # }
    # array_data_file = { 'AA': 100 }

    # new_word = set()
    # for folder, max_file in array_data_file.iteritems():
    #     print '=======================***%s***=======================' % folder
    #     for index_file in range(0, max_file):
    #         if index_file < 10:
    #             file_name = '0' + str(index_file)
    #         else:
    #             file_name = str(index_file)
    #         print 'Start handle data in file %s in folder %s' % (file_name, folder)

    #         wiki_data_path = '/viwiki_data/' + folder + '/wiki_' + file_name
    #         wiki_data_path = module_path + wiki_data_path
    #         doc_array = Helper.load_wiki_data(wiki_data_path)

    #         position_file = '%s_%s' % (folder, file_name)

    #         for index, doc in enumerate(doc_array):
    #             print 'Start training in doc %i of file %s' % (index, folder)
    #             article = Article(doc, position_file, hmm_dictionary)
    #             article.detect_paragraph()
    #             for paragraph in article.paragraphs:
    #                 for sentence in paragraph:
    #                     sentence = sentence.lower()
    #                     array_syllables = sentence.split()

    #                     sentence_object = Article(sentence, position_file, hmm_dictionary)
    #                     sentence_code = sentence_object.convert_syllable_to_number()[0]
    #                     sentence_code = list(map(lambda code: [code], sentence_code))
    #                     predict_tags = model.predict(sentence_code)

    #                     array_word = []
    #                     detect_word = []
    #                     for index, predict_tag in enumerate(predict_tags):
    #                         if predict_tag == 0:
    #                             if detect_word:
    #                                 array_word.append('_'.join(detect_word))
    #                             detect_word = [array_syllables[index]]
    #                         else:
    #                             detect_word.append(array_syllables[index])
    #                     array_word.append('_'.join(detect_word))

    #                     for word in array_word:
    #                         if word in vlsp_word_array:
    #                             continue
    #                         if word in new_word:
    #                             continue
    #                         syllables = word.split('_')
    #                         check_vietnamese = True
    #                         for syllable in syllables:
    #                             if syllable not in syllables_dictionary:
    #                                 check_vietnamese = False
    #                                 break
    #                         if not check_vietnamese:
    #                             continue
    #                         if len(syllables) > 2:
    #                             continue
    #                         new_word.add(word)

    #         new_word_text_file = module_path + '/result_data/hmmlearn_unsupervised_new_word.txt'
    #         file = open(new_word_text_file, "w")

    #         for word in new_word:
    #             file.write(word + '\n')
    #         file.close()
