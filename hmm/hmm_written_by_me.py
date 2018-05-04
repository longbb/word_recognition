# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import csv
import threading
import time

class HiddenMarkovModel(object):
    def __init__(self, states, observations, transitions, emissions,
        start_probabilities):
        self.states = states
        self.observations = observations
        self.transitions = transitions
        self.emissions = emissions
        self.start_probabilities = start_probabilities

    def forward_algorithm(self, observations_sequence):
        forward_matrix = []

        for index_observation, observation in enumerate(observations_sequence):
            forward_array = []

            if index_observation == 0:
                for index_state, state in enumerate(self.states):
                    alpha_i = self.start_probabilities[index_state] * \
                        self.emissions[index_state][observation]
                    forward_array.append(alpha_i)
            else:
                alpha_previous_states = forward_matrix[-1]
                for index_state, state in enumerate(self.states):
                    alpha_i = 0
                    for index_previous_state, alpha_previous_state in enumerate(\
                        alpha_previous_states):
                        alpha_i += alpha_previous_state * \
                            self.transitions[index_previous_state][index_state]
                    alpha_i *= self.emissions[index_state][observation]
                    forward_array.append(alpha_i)
            forward_matrix.append(forward_array)

        final_probabilities = 0
        last_forward_matrix = forward_matrix[-1]
        # end_probabilities = list(map(lambda transition: transition[-1], self.transitions))
        end_probabilities = list(map(lambda state: 1, self.states))
        for index, state in enumerate(self.states):
            final_probabilities += last_forward_matrix[index] * \
                end_probabilities[index]
        return {
            'final_probabilities': final_probabilities,
            'forward_matrix': forward_matrix
        }

    def backward_algorithm(self, observations_sequence):
        backward_matrix = []
        inverse_observations_sequence = observations_sequence[::-1]

        end_probabilities = list(map(lambda state: 1, self.states))
        # end_probabilities = list(map(lambda transition: transition[-1], self.transitions))
        backward_matrix.append(end_probabilities)
        for index_observation, observation in enumerate(inverse_observations_sequence):
            if index_observation == 0:
                continue
            previous_observation = inverse_observations_sequence[\
                index_observation - 1]
            backward_array = []
            beta_previous_states = backward_matrix[-1]
            for index_state, state in enumerate(self.states):
                beta_i = 0
                for index_previous_state, beta_previous_state in enumerate(\
                    beta_previous_states):
                    beta_i += beta_previous_state * \
                        self.transitions[index_state][index_previous_state] * \
                        self.emissions[index_previous_state][previous_observation]
                backward_array.append(beta_i)
            backward_matrix.append(backward_array)

        final_probabilities = 0
        last_backward_matrix = backward_matrix[-1]
        first_observation = observations_sequence[0]
        end_probabilities = list(map(lambda transition: transition[-1], self.transitions))
        for index, state in enumerate(self.states):
            final_probabilities += self.start_probabilities[index] * \
                last_backward_matrix[index] * \
                self.emissions[index][first_observation]
        return {
            'final_probabilities': final_probabilities,
            'backward_matrix': backward_matrix[::-1]
        }

    def veterbi_algorithm(self, observations_sequence):
        veterbi_matrix = []
        backtrace_matrix = []

        for index_observation, observation in enumerate(observations_sequence):
            veterbi_array = []
            backtrace_array = []

            if index_observation == 0:
                for index_state, state in enumerate(self.states):
                    alpha_i = self.start_probabilities[index_state] * \
                        self.emissions[index_state][observation]
                    beta_i = 0
                    veterbi_array.append(alpha_i)
                    backtrace_array.append(beta_i)
            else:
                alpha_previous_states = veterbi_matrix[-1]
                for index_state, state in enumerate(self.states):
                    for index_previous_state, alpha_previous_state in enumerate(\
                        alpha_previous_states):
                        new_alpha_i = alpha_previous_state * \
                            self.transitions[index_previous_state][index_state] * \
                            self.emissions[index_state][observation]

                        if index_previous_state == 0:
                            alpha_i = new_alpha_i
                            beta_i = index_previous_state
                        elif alpha_i < new_alpha_i:
                            alpha_i = new_alpha_i
                            beta_i = index_previous_state

                    veterbi_array.append(alpha_i)
                    backtrace_array.append(beta_i)
            veterbi_matrix.append(veterbi_array)
            backtrace_matrix.append(backtrace_array)

        best_score = 0
        last_veterbi_matrix = veterbi_matrix[-1]
        end_probabilities = list(map(lambda state: 1, self.states))
        for index, state in enumerate(self.states):
            final_score = last_veterbi_matrix[index] * \
                end_probabilities[index]
            if index == 0:
                best_score = final_score
                last_state = state
            elif best_score < final_score:
                best_score = final_score
                last_state = state

        #get state sequence with the highest probability
        states_sequence = [last_state]
        for index in range(1, len(backtrace_matrix))[::-1]:
            back_state = states_sequence[-1]
            states_sequence.append(backtrace_matrix[index][back_state])
        return states_sequence[::-1]

    def baum_welch_algorithm(self, list_observations_sequence, number_thread):
        check_convergence = False
        iteration_number = 1
        sub_list_observations_sequence = []
        for index_observation_sequence, observations_sequence in \
            enumerate(list_observations_sequence):
            if index_observation_sequence < number_thread:
                sub_list_observations_sequence.append([observations_sequence])
            else:
                index_sub = index_observation_sequence % number_thread
                sub_list_observations_sequence[index_sub].append(observations_sequence)
        while not check_convergence:
            print '===================*Iteration %i*===================' % iteration_number
            list_counting = []

            start_time = time.time()
            thread_array = []
            for sub_list in sub_list_observations_sequence:
                thread_array.append(threading.Thread(
                    target=self.counting_emissions_and_transition,
                    args=(sub_list, list_counting,)
                ))
                thread_array[-1].start()
            for thread in thread_array:
                thread.join()
            end_time = time.time()
            print 'Processing time: %f' % (end_time - start_time)

            counting_emissions = list_counting[0][0]
            counting_transition = list_counting[0][1]
            for index_counting, counting in enumerate(list_counting):
                if index_counting == 0:
                    continue
                counting_emissions = self.sum_counting(counting_emissions, counting[0])
                counting_transition = self.sum_counting(counting_transition, counting[1])

            #calculate new emission matrix
            new_emisssion_matrix = []
            for index_state, state_emission in enumerate(counting_emissions):
                # import pdb; pdb.set_trace()
                if index_state == len(self.states) - 1:
                    new_state_emission_probabilities = [0] * len(observations)
                    new_state_emission_probabilities[0] = 1
                else:
                    state_emission[0] = 0
                    total_count = 0
                    for observation_emission in state_emission:
                        total_count += observation_emission

                    new_state_emission_probabilities = []
                    for observation_emission in state_emission:
                        new_state_emission_probabilities.append(observation_emission / \
                            total_count)
                new_emisssion_matrix.append(new_state_emission_probabilities)

            #calculatate new emission matrix
            new_transition_matrix = []
            for state_transaction in counting_transition:
                total_count = 0
                for next_step_transacion in state_transaction:
                    total_count += next_step_transacion

                new_state_transaction_probabilities = []
                for next_step_transacion in state_transaction:
                    new_state_transaction_probabilities.append(next_step_transacion / \
                        total_count)
                new_transition_matrix.append(new_state_transaction_probabilities)
            new_transition_matrix[-1] = [1, 0, 0]

            check_convergence = self.__check_convergence(new_emisssion_matrix,
                new_transition_matrix)
            self.transitions = new_transition_matrix
            self.emissions = new_emisssion_matrix
            iteration_number += 1

    def counting_emissions_and_transition(self, list_observations_sequence, list_counting):
        # print 'Start thread at: %f' % time.time()
        counting_emissions = []
        counting_transition = []
        for state in self.states:
            emisstion_zero_arrays = [0] * len(self.observations)
            counting_emissions.append(emisstion_zero_arrays)

            transition_zero_arrays = [0] * len(self.states)
            counting_transition.append(transition_zero_arrays)

        for observations_sequence in list_observations_sequence:
            forward_matrix = self.forward_algorithm(observations_sequence)

            final_probabilities = forward_matrix['final_probabilities']
            forward_matrix = forward_matrix['forward_matrix']

            backward_matrix = self.backward_algorithm(observations_sequence)
            backward_matrix = backward_matrix['backward_matrix']

            if final_probabilities == 0:
                continue
            #caculate P(h_t=i, X)
            for index_observation, observation in enumerate(observations_sequence):
                concurrent_probability_i = []
                for index_state, state in enumerate(self.states):
                    concurrent_probability_it = forward_matrix[index_observation][\
                        index_state] * backward_matrix[index_observation][index_state]
                    concurrent_probability_it /= final_probabilities
                    counting_emissions[index_state][observation] += concurrent_probability_it

            #caculate P(h_t=i, h_t+1=j, X)
            for index_observation, observation in enumerate(observations_sequence):
                if index_observation == len(observations_sequence) - 1:
                    continue
                current_forward = forward_matrix[index_observation]
                next_backward = backward_matrix[index_observation + 1]
                for index_state, state in enumerate(self.states):
                    for index_next_state, state in enumerate(self.states):
                        transition_probability_ijt = current_forward[index_state] * \
                            self.transitions[index_state][index_next_state] * \
                            next_backward[index_next_state]
                        transition_probability_ijt /= final_probabilities

                        counting_transition[index_state][index_next_state] += \
                            transition_probability_ijt
        # print 'End thread at: %f' % time.time()

        return list_counting.append([counting_emissions, counting_transition])

    def sum_counting(self, counting_1, counting_2):
        for index_state, states_conting in enumerate(counting_1):
            for index_observation, observation_conting in enumerate(states_conting):
                counting_1[index_state][index_observation] += \
                    counting_2[index_state][index_observation]
        return counting_1

    def __check_convergence(self, new_emisssion_matrix, new_transition_matrix):
        emission_change = 0
        for index_state, state_emission in enumerate(new_emisssion_matrix):
            for index_observation, observation_emission in enumerate(state_emission):
                emission_change += abs(observation_emission - \
                    self.emissions[index_state][index_observation])

        transition_change = 0
        for index_state, state_transaction in enumerate(new_transition_matrix):
            for index_next_state, next_step_transacion in enumerate(state_transaction):
                transition_change += abs(next_step_transacion - \
                    self.transitions[index_state][index_next_state])

        print 'Emission change: %f' % emission_change
        print 'transition_change: %f' % transition_change

        check = (emission_change < 0.1) and (transition_change < 0.1)
        return check

if __name__ == '__main__':
    # states = [0, 1]
    # observations = [0, 1, 2]
    # transitions = [[0.6, 0.4], [0.5, 0.5]]
    # emissions = [[0.2, 0.4, 0.4], [0.5, 0.4, 0.1]]

    # start_probabilities = [0.8, 0.2]
    # hmm = HiddenMarkovModel(states, observations, transitions, emissions, \
    #     start_probabilities)
    # # forward_probability = hmm.forward_algorithm([2, 0, 2])
    # # backward_probability = hmm.backward_algorithm([2, 0, 2])
    # # hmm.baum_welch_algorithm([[2, 0, 1, 2, 1, 2, 0, 0, 0, 0, 1, 0, 1, 0, 2], [1, 0, 1, 2, 1, 1, 2, 1, 2, 0, 0], [2, 2, 0, 1, 0, 2]], 3)
    # sequence_states = hmm.veterbi_algorithm([2, 0, 2])
    # import pdb; pdb.set_trace()

    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    syllables_dictionary = Helper.load_syllables_dictionary(output_option='dict')
    c_l_e_path = module_path + '/data/c_e_l_viettreebank.txt'
    dictionary_file = open(c_l_e_path, "r")
    c_l_e_labels = set()
    for line in dictionary_file:
        word = line[:-1].decode('utf8')
        c_l_e_labels.add(word)
    # c_l_e_labels = Helper.load_obj(c_l_e_path)

    # start build dict for training
    symbol_appeared = {}
    number_appeared = 1
    number_article = 0
    number_sentence = 0
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
                article.detect_paragraph()
                number_article += 1
                for paragraph in article.paragraphs:
                    for sentence in paragraph:
                        number_sentence += 1
                        sentence = sentence[0].lower() + sentence[1:]
                        sentence_training_data = []
                        syllables = sentence.split()
                        for syllable in syllables:
                            if syllable not in syllables_dictionary:
                                continue
                            if syllable.decode('utf-8') in c_l_e_labels:
                                continue
                            if syllable in symbol_appeared:
                                continue
                            symbol_appeared[syllable] = number_appeared
                            number_appeared += 1

    symbol_appeared['NOT_VIETNAMESE'] = 0

    hmm_by_me_dictionary_path = module_path + '/hmm/hmm_data/hmm_by_me_dictionary_without_cle_all.pkl'
    save_data = Helper.save_obj(symbol_appeared, hmm_by_me_dictionary_path)
    print 'Number article: %i' % number_article
    print 'Number sentence: %i' % number_sentence

    print 'Start training'
    observations_sequence = []
    number_doc_passed = 0
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
                observations_sequence.extend(article_unlabeled_sequences)
                number_doc_passed += 1
    observations_sequence = list(filter(lambda observation_sequence: \
        len(observation_sequence) > 2, observations_sequence))

    states = [0, 1, 2]
    observations = range(0, len(symbol_appeared))
    transitions = [[0.45, 0.35, 0.2], [0.6, 0.2, 0.2], [1, 0, 0]]
    emissions = []
    for index_state, state in enumerate(states):
        states_emission = []
        if index_state == len(states) - 1:
            for index_observation, observation in enumerate(observations):
                if index_observation == 0:
                    states_emission.append(1)
                else:
                    states_emission.append(0)
        else:
            avg_probability = float(1) / (len(observations) - 1)
            for index_observation, observation in enumerate(observations):
                if index_observation == 0:
                    states_emission.append(0)
                else:
                    states_emission.append(avg_probability)
        emissions.append(states_emission)
    start_probabilities = [0.7, 0, 0.3]
    hmm = HiddenMarkovModel(states, observations, transitions, emissions, \
        start_probabilities)
    hmm.baum_welch_algorithm(observations_sequence, 1)
    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_by_me_without_cle_all.pkl'
    Helper.save_obj(hmm, hmm_save_path)
    import pdb; pdb.set_trace()
