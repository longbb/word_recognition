# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import math
from hmm import HiddenMarkovModel
import csv
import nltk
import dill

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_model.dill'
    hmm_tagger = HiddenMarkovModel()
    hmm_tagger.load_model(hmm_save_path)
    import pdb; pdb.set_trace()

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
    array_data_file = { 'AA': 2 }
    syllables_dictionary = Helper.load_syllables_dictionary()

    new_word = set()
    for folder, max_file in array_data_file.iteritems():
        print '=======================***%s***=======================' % folder
        for index_file in range(0, max_file):
            if index_file < 10:
                file_name = '0' + str(index_file)
            else:
                file_name = str(index_file)
            print 'Start handle data in file %s in folder %s' % (file_name, folder)

            wiki_data_path = '/viwiki_data/' + folder + '/wiki_' + file_name
            wiki_data_path = module_path + wiki_data_path
            doc_array = Helper.load_wiki_data(wiki_data_path)

            position_file = '%s_%s' % (folder, file_name)

            for index, doc in enumerate(doc_array):
                print 'Start training in doc %i of file %s' % (index, folder)
                article = Article(doc, position_file, syllables_dictionary)
                article.detect_paragraph()
                for paragraph in article.paragraphs:
                    for sentence in paragraph:
                        sentence = sentence[0].lower() + sentence[1:]
                        array_word = hmm_tagger.word_recognition(sentence)
                        for word in array_word:
                            if word in vlsp_word_array:
                                continue
                            if word in new_word:
                                continue
                            syllables = word.split('_')
                            check_vietnamese = True
                            for syllable in syllables:
                                if syllable not in syllables_dictionary:
                                    check_vietnamese = False
                                    break
                            if not check_vietnamese:
                                continue
                            if len(syllables) > 2:
                                continue
                            new_word.add(word)

            new_word_text_file = module_path + '/result_data/hmm_unsupervised_new_word.txt'
            file = open(new_word_text_file, "w")

            for word in new_word:
                file.write(word + '\n')
            file.close()
