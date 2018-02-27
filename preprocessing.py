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
    # number_done = int(sys.argv[1])

    # # create bigram database
    # bigram_database = Database('bigram_collection')
    # bigram_database.collection.drop_indexes()
    # bigram_database.collection.create_index([('key_word', pymongo.ASCENDING)], unique=True)

    # # create sentence database
    # sentence_database = Database('sentence_collection')
    # sentence_database.collection.drop_indexes()
    # sentence_database.collection.create_index([('article_index', pymongo.ASCENDING)], unique=True)

    # # create word database
    # word_database = Database('word_collection')
    # word_database.collection.drop_indexes()
    # word_database.collection.create_index([('key_word', pymongo.ASCENDING)], unique=True)

    # # load training data
    # module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
    #     '/word_recognition'
    # path_to_csv_file = module_path + '/data/articles.csv'
    # csv.field_size_limit(sys.maxsize)
    # dataset = Helper.read_file_csv(path_to_csv_file)
    # path_to_csv_file = module_path + '/data/articles_new.csv'
    # dataset.extend(Helper.read_file_csv(path_to_csv_file))

    # # preprocessing
    # number_document_done = 0
    # for index, data in enumerate(dataset):
    #     if index >= number_done:
    #         content = (data[2] + '\n' + data[4])
    #         content = content.decode('utf-8')
    #         article_module = Article(content, index)
    #         bigram_hash = article_module.get_bigram()

    #         # write bigram data to database
    #         for key, value in bigram_hash.iteritems():
    #             find_bigram = bigram_database.find_one({
    #                 'key_word': key
    #             })
    #             if find_bigram['success'] and find_bigram['object']:
    #                 data_in_database = find_bigram['object']
    #                 new_data = Helper.merge_two_data(data_in_database['data'], value)
    #                 update_bigram = bigram_database.update({
    #                     '_id': data_in_database['_id']
    #                 }, {
    #                     'key_word': data_in_database['key_word'],
    #                     'data': new_data
    #                 })
    #             else:
    #                 create_bigram = bigram_database.create({
    #                     'key_word': key,
    #                     'data': value
    #                 })

    #         # write sentence data to database
    #         array_sentences = []
    #         for  paragraph in article_module.paragraphs:
    #             array_sentences.extend(paragraph)
    #         create_bigram = sentence_database.create({
    #             'article_index': index,
    #             'data': array_sentences
    #         })

    #     number_document_done += 1
    #     print '%s / %s document done' % (str(number_document_done), str(len(dataset)))


    # number_unigram_occurrences = 0
    # number_bigram_occurrences = 0
    # bigrams = bigram_database.collection.find()
    # for bigram in bigrams:
    #     if bigram['key_word'] not in ['SYSTEM_CODE|NUMBER_BIGRAM_OCCURRENCES',
    #         'SYSTEM_CODE|NUMBER_UNIGRAM_OCCURRENCES']:
    #         number_unigram_occurrences += bigram['data']['number_occurrences']
    #         for key, value in bigram['data'].iteritems():
    #             if key == 'number_occurrences':
    #                 continue
    #             number_bigram_occurrences += value['number_occurrences']

    # find_number_unigram = bigram_database.find_one({ 'key_word': 'SYSTEM_CODE|NUMBER_UNIGRAM_OCCURRENCES' })
    # if not find_number_unigram['success']:
    #     print 'Has an exception: %s' % str(find_number_unigram['message'])
    # if find_number_unigram['object']:
    #     bigram_database.update({
    #         '_id': find_number_unigram['object']['_id']
    #     } ,{
    #         'key_word': 'SYSTEM_CODE|NUMBER_UNIGRAM_OCCURRENCES',
    #         'data': number_unigram_occurrences
    #     })
    # else:
    #     bigram_database.create({
    #         'key_word': 'SYSTEM_CODE|NUMBER_UNIGRAM_OCCURRENCES',
    #         'data': number_unigram_occurrences
    #     })

    # find_number_bigram = bigram_database.find_one({ 'key_word': 'SYSTEM_CODE|NUMBER_BIGRAM_OCCURRENCES' })
    # if not find_number_bigram['success']:
    #     print 'Has an exception: %s' % str(find_number_bigram['message'])
    # if find_number_bigram['object']:
    #     bigram_database.update({
    #         '_id': find_number_bigram['object']['_id']
    #     } ,{
    #         'key_word': 'SYSTEM_CODE|NUMBER_BIGRAM_OCCURRENCES',
    #         'data': number_bigram_occurrences
    #     })
    # else:
    #     bigram_database.create({
    #         'key_word': 'SYSTEM_CODE|NUMBER_BIGRAM_OCCURRENCES',
    #         'data': number_bigram_occurrences
    #     })

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
    total_bigram_hash = {}
    total_file = 0

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
    print 'Handle done %i doc' % total_file

    print 'Save data to file'
    result_data_path = module_path + '/result_data/bigram.pkl'
    Helper.save_obj(total_bigram_hash, result_data_path)
    print 'Save done!'
