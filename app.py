'''
WebApp built on PyText to detect intents and slots in queries.

Largely based on:
https://pytext-pytext.readthedocs-hosted.com/en/latest/atis_tutorial.html
'''

import sys
import flask
import pytext

# The configuration file distributed in this package.
config = pytext.load_config('atis_config.json')
# The PyText predictor object. The prediction model file is distributed in this package.
predictor = pytext.create_predictor(config, 'atis_model.c2')

app = flask.Flask(__name__)

@app.route('/get_flight_info', methods=['POST'])
def get_flight_info():
    """
    Single RESTful endpoint exposed with this app.
    
    Payload
    -------
    A plain text via a POST request.

    Returns
    -------
        * If no text is supplied: a JSON containing an error message.
        * If text is supplied: a JSON containing the intent and the slots.

    """

    text = flask.request.data.decode()

    if text is None or text == '':
        return flask.jsonify(error="No query supplied.")

    result = predictor({"raw_text": text})

    return flask.jsonify(intent=getIntent(result), slots=getSlots(text, result))

def getIntent(result):
    """
    Gets the intent with the highest score from the result object.
    
    Parameters
    ----------
        The result object.

    Returns
    -------
        A string representing the intent. For example:
            'flight'

    """

    return max((label for label in result if label.startswith(
        "doc_scores:")), key=lambda label: result[label][0],)[len("doc_scores:"):]

def getSlots(text, result):
    """
    Gets the the highest meaningful slot for each token in the result object.
    
    Parameters
    ----------
        The supplied raw text.
        The result object.

    Returns
    -------
        A dictionary where keys are all those tokens whose most probable slot is not 'NoLabel'. For example:
            {'cost_relative': 'cheapest', 'toloc.city_name': 'new york city', 'depart_date.month_name': 'march 24th', 'depart_time.period_of_day': 'morning'}

    """

    tokens = text.split()
    tokenLabels = dict.fromkeys(tokens)
    for label in result:
        if label.startswith("word_scores:"):
            scores = result[label].tolist()
            for score in scores:
                scoreValue = score[0]
                trimmedLabel = label[len("word_scores:"):]
                token = tokens[scores.index(score)]
                if tokenLabels[token] is None:
                    tokenLabels[token] = {}
                    tokenLabels[token]['label'] = trimmedLabel
                    tokenLabels[token]['score'] = scoreValue
                elif tokenLabels[token]['score'] < scoreValue:
                    tokenLabels[token]['label'] = trimmedLabel
                    tokenLabels[token]['score'] = scoreValue

    slots = {}
    for token in tokenLabels:
        if tokenLabels[token]['label'] != 'NoLabel':
            slot = tokenLabels[token]['label']
            if slot not in slots:
                slots[slot] = token
            else:
                slots[slot] += " " + token
    return slots