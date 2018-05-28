# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from flask import Flask, render_template, request, json
from hmm.hmm_written_by_me import HiddenMarkovModel
from helper import Helper

app = Flask(__name__)
module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
syllables_dictionary = Helper.load_syllables_dictionary()

hmm_by_me_dictionary_path = module_path + '/hmm/hmm_data/hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
hmm_dictionary = Helper.load_obj(hmm_by_me_dictionary_path)

invert_dictionary_path = module_path + '/hmm/hmm_data/invert_hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
invert_hmm_dictionary = Helper.load_obj(invert_dictionary_path)

hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_by_me_without_cle_all_new_dict.pkl'
hmm = Helper.load_obj(hmm_save_path)

occurrences_data_path = module_path + '/result_data/occurrences.pkl'
statistic_bigram = Helper.load_obj(occurrences_data_path)

#test with sub parameter
bigram_path = module_path + '/hmm/hmm_data/bigram.pkl'
bigram_hash = Helper.load_obj(bigram_path)
invert_bigram_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
invert_bigram_hash = Helper.load_obj(invert_bigram_path)


@app.route('/')
def hello_world():
    return render_template('ui.html')

@app.route('/word_segment')
def word_segment():
    article = request.args.get('article')
    segmented_article = hmm.word_segment(
        article,
        using_sub_params=True,
        bigram_hash=bigram_hash,
        invert_bigram_hash=invert_bigram_hash,
        number_occurrences=statistic_bigram,
        dictionary=hmm_dictionary,
        invert_dictionary=invert_hmm_dictionary
    )
    result = json.dumps({
        'status': 'success',
        'article': segmented_article
    })
    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == '__main__':
    app.run(debug = True)
