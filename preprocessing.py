# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import csv
import pymongo
from pymongo import MongoClient

if __name__ == '__main__':
    array_data_file = {
        'AA': 100,
        'AB': 100,
        'AC': 100,
        'AD': 100,
        'AE': 100,
        'AF': 100,
        'AG': 100,
        'AH': 82
    }
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    syllables_dictionary = Helper.load_syllables_dictionary()
    hmm_by_me_dictionary_path = module_path + '/hmm/hmm_data/hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
    syllables_dictionary = Helper.load_obj(hmm_by_me_dictionary_path)
    total_bigram_hash = {}
    total_file = 0

    # find bigram in viwiki
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
                article = Article(doc, position_file, syllables_dictionary)
                bigram_hash = article.get_bigram()
                total_bigram_hash = Helper.merge_two_data(bigram_hash, total_bigram_hash)
                print 'Doc %i in file %s in folder %s done' % (index, file_name, folder)
                total_file += 1

    # vlsp_folder_path = module_path + '/VLSP_Sentences/train'
    # files = os.listdir(vlsp_folder_path)
    # doc_array = []
    # for file in files:
    #     posts = Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file)
    #     doc = '\n'.join(posts)
    #     doc = doc.replace("_", " ")
    #     doc_array.append(doc)

    # for index, doc in enumerate(doc_array):
    #     article = Article(doc, index, syllables_dictionary)
    #     bigram_hash = article.get_bigram()
    #     total_bigram_hash = Helper.merge_two_data(bigram_hash, total_bigram_hash)
    #     total_file += 1
    # print 'Handle done %i doc' % total_file

    print 'Save data to file'
    result_data_path = module_path + '/hmm/hmm_data/bigram.pkl'
    Helper.save_obj(total_bigram_hash, result_data_path)
    print 'Save done!'

    number_unigram_occurrences = 0
    number_bigram_occurrences = 0
    for unigram, unigram_info in total_bigram_hash.iteritems():
        number_unigram_occurrences += unigram_info['number_occurrences']
        for bigram, bigram_info in unigram_info.iteritems():
            if bigram == 'number_occurrences':
                continue
            number_bigram_occurrences += bigram_info['number_occurrences']

    statistic_bigram = {
        'number_unigram_occurrences': number_unigram_occurrences,
        'number_bigram_occurrences': number_bigram_occurrences
    }
    print statistic_bigram
    occurrences_data_path = module_path + '/hmm/hmm_data/occurrences.pkl'
    Helper.save_obj(statistic_bigram, occurrences_data_path)

    # find invert_bigram_hash with key is behind word of bigram in viwiki
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
                article = Article(doc, position_file, syllables_dictionary)
                bigram_hash = article.invert_bigram()
                total_bigram_hash = Helper.merge_two_data(bigram_hash, total_bigram_hash)
                print 'Doc %i in file %s in folder %s done' % (index, file_name, folder)
                total_file += 1

    # for index, doc in enumerate(doc_array):
    #     article = Article(doc, index, syllables_dictionary)
    #     bigram_hash = article.invert_bigram()
    #     total_bigram_hash = Helper.merge_two_data(bigram_hash, total_bigram_hash)
    #     total_file += 1
    # print 'Handle done %i doc' % total_file

    print 'Save data to file'
    result_data_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    Helper.save_obj(total_bigram_hash, result_data_path)
    print 'Save done!'

    # load data and get number occurrences in bigram of word
    bigram_path = module_path + '/hmm/hmm_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    invert_bigram_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    invert_bigram_hash = Helper.load_obj(invert_bigram_path)

    for word, hash_info in bigram_hash.iteritems():
        number_occurrences_in_bigram = 0
        for key, value in hash_info.iteritems():
            if key == 'number_occurrences':
                continue
            number_occurrences_in_bigram += value['number_occurrences']
        bigram_hash[word]['number_occurrences_in_bigram'] = number_occurrences_in_bigram
    print 'Save data to file'
    result_data_path = module_path + '/hmm/hmm_data/bigram.pkl'
    Helper.save_obj(bigram_hash, result_data_path)
    print 'Save done!'

    for word, hash_info in invert_bigram_hash.iteritems():
        number_occurrences_in_bigram = 0
        for key, value in hash_info.iteritems():
            if key == 'number_occurrences':
                continue
            number_occurrences_in_bigram += value['number_occurrences']
        invert_bigram_hash[word]['number_occurrences_in_bigram'] = number_occurrences_in_bigram
    print 'Save data to file'
    result_data_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    Helper.save_obj(invert_bigram_hash, result_data_path)
    print 'Save done!'

    # calculate average number_occurrences
    bigram_path = module_path + '/hmm/hmm_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    invert_bigram_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    invert_bigram_hash = Helper.load_obj(invert_bigram_path)

    for word, hash_info in bigram_hash.iteritems():
        if len(hash_info) == 2:
            avg_number_occurrences = 0.001
        else:
            avg_number_occurrences = float(hash_info['number_occurrences_in_bigram']) / \
                (len(hash_info) - 2)
        bigram_hash[word]['avg_number_occurrences'] = avg_number_occurrences
    print 'Save data to file'
    result_data_path = module_path + '/hmm/hmm_data/bigram.pkl'
    Helper.save_obj(bigram_hash, result_data_path)
    print 'Save done!'

    for word, hash_info in invert_bigram_hash.iteritems():
        if len(hash_info) == 2:
            avg_number_occurrences = 0.001
        else:
            avg_number_occurrences = float(hash_info['number_occurrences_in_bigram']) / \
                (len(hash_info) - 2)
        invert_bigram_hash[word]['avg_number_occurrences'] = avg_number_occurrences
    print 'Save data to file'
    result_data_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    Helper.save_obj(invert_bigram_hash, result_data_path)
    print 'Save done!'
