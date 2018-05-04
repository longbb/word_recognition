# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import csv
import nltk
import dill

class HiddenMarkovModel(object):
    def __init__(self, model=None, trainer=None):
        self.model = model
        self.trainer = trainer

    def train_unsupervised(self, unlabeled_sequences):
        if self.model:
            new_model = self.trainer.train_unsupervised(unlabeled_sequences, max_iterations = 10,
                model=self.model)
        else:
            new_model = self.trainer.train_unsupervised(unlabeled_sequences, max_iterations = 10)
        return new_model

    def train_supervised(self, labeled_sequence):
        new_model = self.trainer.train_supervised(labeled_sequence)
        return new_model

    def predict(self, unlabeled_sequences):
        if not self.model:
            return unlabeled_sequences
        return self.model.tag(unlabeled_sequences)

    def word_recognition(self, sentence):
        syllable_array = sentence.split()
        predict_tags = self.predict(syllable_array)
        word_array = []
        new_word = []
        for predict_tag in predict_tags:
            if predict_tag[1] == 0:
                if new_word:
                    word_array.append('_'.join(new_word))
                new_word = [predict_tag[0]]
            else:
                new_word.append(predict_tag[0])
        return word_array

    def save_model(self, path_to_save, model):
        with open(path_to_save, 'wb') as f:
            dill.dump(model, f)

    def load_model(self, path_to_save):
        with open(path_to_save, 'rb') as f:
            hmm_tagger = dill.load(f)
        self.model = hmm_tagger
        return hmm_tagger

    def caculate_precesion(self, unlabeled_sequence, labeled_sequence):
        try:
            if len(unlabeled_sequence) != len(labeled_sequence):
                return {
                    'success': False,
                    'message': 'unlabeled_sequence and labeled_sequence do not match'
                }
            predict_tags = self.predict(unlabeled_sequence)
            predict_tags = list(map(lambda predict_tag: predict_tag[1], predict_tags))

            number_predict_true = 0
            for index, predict_tag in enumerate(predict_tags):
                if index >= len(labeled_sequence):
                    continue
                if labeled_sequence[index] == predict_tag:
                    number_predict_true += 1

            return {
                'success': True,
                'object': float(number_predict_true) / len(predict_tags)
            }
        except Exception as error:
            return {
                'success': False,
                'message': str(error)
            }
