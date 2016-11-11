#!/usr/bin/python2.7

from nltk.corpus import names
import random
import nltk


def build_new_file_path(filepath, outpath):
    # get just the input filename to build the corresponding output file
    # path
    filename = filepath.split('.')[0].split('/')[-1]
    outfilename = outpath + '/' + filename + '.response'
    return outfilename


# calculates edit distances between two strings
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/
#         Levenshtein_distance#Python
def lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    return min(lev(a[1:], b[1:]) + (a[0] != b[0]),
               lev(a[1:], b) + 1,
               lev(a, b[1:]) + 1)


# returns singular, plural, or 'None' for a given pos.
def get_number(pos):
    numberDict = {"NN": "singular",
                  "NNP": "singular",
                  "he": "singular",
                  "she": "singular",
                  "him": "singular",
                  "her": "singular",
                  "it": "singular",
                  "himself": "singular",
                  "herself": "singular",
                  "itself": "singular",
                  "NNS": "plural",
                  "NNPS": "plural",
                  "they": "plural",
                  "them": "plural",
                  "themselves": "plural",
                  "PRP": None}

    if pos in numberDict:
        return numberDict[pos]
    else:
        return None


# check for gender agreement
def get_gender(string):
    labeled_names = ([(name, 'male') for name in names.words('male.txt')] +
                     [(name, 'female') for name in names.words('female.txt')])
    random.shuffle(labeled_names)

    def gender_features(word):
        return {'last_letter': word[-1]}

    featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
    train_set, test_set = featuresets[500:], featuresets[:500]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    return classifier.classify(gender_features(string))


# generates a random unique identifier
def generate_coref_id(length=5):
    key = ''.join(random.choice('ABCDEF0123456789') for i in range(length))
    return key


# inserts a REF attribute to a coreference tag in data
def insert_coref_tag(data, coref_id, ref):
    tag = '<COREF ID="%s"' % coref_id
    # find coref in original text
    pos_in_text = data.find(tag) + len(tag)
    # smash the new reference id into the original file data
    data = '%s REF="%s"%s' % (data[:pos_in_text], ref['id'], data[pos_in_text:])
    return data


# indicates if the noun phrase beginning at `noun_phrase_index` is between
# existing open/close COREF xml tags
def nested_noun_phrase(sub_data, noun_phrase_index):
    data_position = 0
    while len(sub_data) > 1:
        open_tag_index = sub_data.find("<COREF ") + data_position
        sub_data_close_index = sub_data.find("</COREF>")
        close_tag_index = sub_data_close_index + data_position

        # if the first opening tag comes after the first closing tag
        if open_tag_index > close_tag_index:
            return True

        # if the new noun phrase is between existing coref tags, skip
        if open_tag_index <= noun_phrase_index and noun_phrase_index <= close_tag_index:
            return True

        # the new noun phrase index comes before the point we're at,
        # so we've looked far enough and not found a problem
        if noun_phrase_index < close_tag_index:
            return False

        closing_position = sub_data_close_index + len("</COREF>")
        sub_data = sub_data[closing_position:]
        data_position = data_position + closing_position

    return False
