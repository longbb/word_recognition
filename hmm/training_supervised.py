# coding: utf-8
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

    vlsp_folder_path = module_path + '/VLSP_Sentences/train'
    files = os.listdir(vlsp_folder_path)
    sentences = []

    syllables_dictionary = Helper.load_syllables_dictionary()
    article = Article('', 0, syllables_dictionary)

    total_labeled_sequence = []
    print 'Start read data'
    for file in files:
        sentences.extend(Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file))
    print 'Start build labeled sequence, need handle %i sentences' % len(sentences)
    for index_sentence, sentence in enumerate(sentences):
        print 'Handle for sentence %i' % index_sentence
        labeled_sequence = []
        if not sentence:
            continue
        sentence = sentence[0].lower() + sentence[1:]
        for word in sentence.split():
            syllable_array = word.split('_')
            for index, syllable in enumerate(syllable_array):
                label = 0 if index == 0 else 1
                syllable_type = article.check_type_syllable(syllable)
                if syllable_type == 'VIETNAMESE_SYLLABLE|SYSTEM_CODE':
                    labeled_sequence.append((syllable, label))
                else:
                    labeled_sequence.append((syllable_type, label))
        total_labeled_sequence.append(labeled_sequence)

    syllables_dictionary.update(['FOREIGN_SYLLABLE|SYSTEM_CODE',
        'DIGIT|SYSTEM_CODE', 'CODE|SYSTEM_CODE'])
    symbols = list(syllables_dictionary)
    states = [0, 1]
    trainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=states, symbols=symbols)
    hmm_model = HiddenMarkovModel(None, trainer)
    model = hmm_model.train_supervised(total_labeled_sequence)

    hmm_save_path = module_path + '/hmm/hmm_data/supervised_hmm_model.dill'
    with open(hmm_save_path, 'wb') as f:
        dill.dump(model, f)
