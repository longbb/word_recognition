# coding: utf-8
import os
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import hmmlearn.hmm as hmm
import numpy as np
from sklearn.externals import joblib

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    array_data_file = {
        'AA': 100
    }
    syllables_dictionary = Helper.load_syllables_dictionary(output_option='dict')

    # start build dict for training
    symbol_appeared = {}
    number_appeared = 0
    print 'Start build dictionaty'
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
                article_unlabeled_sequences = article.get_hmm_training()
                for sentence in article_unlabeled_sequences:
                    for syllable_info in sentence:
                        syllable = syllable_info[0]
                        if syllable in symbol_appeared:
                            continue
                        else:
                            symbol_appeared[syllable] = number_appeared
                            number_appeared += 1

    special_codes = ['FOREIGN_SYLLABLE|SYSTEM_CODE', 'DIGIT|SYSTEM_CODE', 'CODE|SYSTEM_CODE']
    for special_code in special_codes:
        if special_code not in symbol_appeared:
            symbol_appeared[special_code] = number_appeared
            number_appeared += 1

    hmm_learn_dictionary_path = module_path + '/hmm/hmm_data/hmm_learn_dictionary.pkl'
    save_data = Helper.save_obj(symbol_appeared, hmm_learn_dictionary_path)

    # start training
    print 'Start training'
    unlabeled_sequences = []
    number_doc_passed = 0
    lengths = []
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
                article = Article(doc, position_file, symbol_appeared)
                article_unlabeled_sequences = article.convert_syllable_to_number()
                for sentence in article_unlabeled_sequences:
                    for syllable in sentence:
                        unlabeled_sequences.append([syllable])
                    lengths.append(len(sentence))

                number_doc_passed += 1

    n_features = len(symbol_appeared)
    n_components = 2
    startprob = np.array([1, 0])
    transmat = np.array([
        [0.5, 0.5],
        [0.9, 0.1]
    ])

    model = hmm.MultinomialHMM(n_components=2, transmat_prior=transmat, params='te',
        init_params='e')
    model.startprob_ = startprob
    # model.n_features = n_features
    model.fit(unlabeled_sequences, lengths)

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmmlearn.pkl'
    joblib.dump(model, hmm_save_path)
