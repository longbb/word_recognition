# coding: utf-8
import os
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
from hmm import HiddenMarkovModel
import csv
import nltk
import dill

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    array_data_file = {
        'AA': 100
    }
    syllables_dictionary = Helper.load_syllables_dictionary()
    total_bigram_hash = {}
    total_file = 0

    syllables_dictionary.update(['FOREIGN_SYLLABLE|SYSTEM_CODE',
        'DIGIT|SYSTEM_CODE', 'CODE|SYSTEM_CODE'])
    symbols = list(syllables_dictionary)
    states = [0, 1]
    model = None
    number_doc_passed = 0
    trainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=states, symbols=symbols)

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_model.dill'
    number_doc_pass_path = module_path + '/hmm/hmm_data/number_doc.txt'
    #check existance of hmm model
    # passed = 0
    # if os.path.exists(hmm_save_path) and os.path.exists(number_doc_pass_path):
    #     hmm_model = HiddenMarkovModel(model, trainer)
    #     model = hmm_model.load_model(hmm_save_path)
    #     passed = open(number_doc_pass_path, 'r').read()
    #     passed = int(passed)

    # number_doc_passed = 0
    unlabeled_sequences = []
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
                # if number_doc_passed < passed:
                #     number_doc_passed += 1
                #     continue
                article = Article(doc, position_file, syllables_dictionary)
                article_unlabeled_sequences = article.get_hmm_training()
                unlabeled_sequences.extend(article_unlabeled_sequences)

                number_doc_passed += 1

                # if number_doc_passed % 100 == 0:
                #     print 'Start save file in doc %i' % number_doc_passed
                #     #save data
                #     hmm_save_path = module_path + '/hmm/hmm_data/hmm_model.dill'
                #     with open(hmm_save_path, 'wb') as f:
                #         dill.dump(model, f)

                #     file = open(number_doc_pass_path, 'wb')
                #     file.write(str(number_doc_passed))
                #     file.close()

    priors = nltk.probability.RandomProbDist(states)
    priors._probs[0] = 1
    priors._probs[1] = 0

    transition_dict = dict()
    b_priors = nltk.probability.RandomProbDist(states)
    b_priors._probs[0] = 0.5
    b_priors._probs[1] = 0.5
    i_priors = nltk.probability.RandomProbDist(states)
    i_priors._probs[0] = 0.9
    i_priors._probs[1] = 0.1
    transition_dict = {
        0: b_priors,
        1: i_priors
    }
    transitions = nltk.probability.DictionaryConditionalProbDist(transition_dict)

    outputs = nltk.probability.DictionaryConditionalProbDist(
        dict((state, nltk.probability.RandomProbDist(symbols))
            for state in states))

    model = nltk.tag.hmm.HiddenMarkovModelTagger(symbols, states,
        transitions, outputs, priors)

    hmm_model = HiddenMarkovModel(model, trainer)
    model = hmm_model.train_unsupervised(unlabeled_sequences)

    print 'Handle done %i doc' % number_doc_passed

    with open(hmm_save_path, 'wb') as f:
        dill.dump(model, f)
