#!/usr/bin/python2.7

from nltk.tokenize import sent_tokenize, word_tokenize
import xml.etree.ElementTree as ET
from nltk.corpus import names
import random
import nltk
import sys
import random
from difflib import SequenceMatcher as editDifference

# Uncomment for first run!
#nltk.download('punkt')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
#nltk.download('names')

#Function to calculate edit distances between two strings - not currently being used
#from : https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def lev(a, b):
    if not a: return len(b)
    if not b: return len(a)
    return min(lev(a[1:], b[1:])+(a[0] != b[0]), lev(a[1:], b)+1, lev(a, b[1:])+1)

# Function that actually finds the coreference from within a list of possible NPs
def find_coref(ind, anaphor, NP_List):  # Fist attempt at coreferencing based on gender, number agreement, and string matching
    # Only consider anaphors/NPs that show up before the current one
    for el in list(reversed(range(ind))):
        coref = NP_List[el]

        if anaphor['text'] == coref['text'] or anaphor['text'].split()[-1] in coref or anaphor['text'].split()[0] in coref[
            'text']:  # String Matching - entire NP or head noun
            # print 'Found on string matching' + anaphor['text'] + '  ' + coref['text']
            return coref

        if editDifference(None, anaphor['text'], coref['text']).ratio() > 0.65:
            return coref

    # TODO: include pronoun resolution
    #No string matching was found, search again, this time with pronoun resolution


    # TODO: include named entity resolution
    #No prior resolution was found, search again, this time with named entity resolution


    # No prior resolution was found, search again, this time with gender and number
    for el in list(reversed(range(ind))):
        coref = NP_List[el]

        if anaphor['gender'] == coref['gender'] and anaphor['number'] == coref[
            'number']:  # check for gender and number, or string agreement
            return coref

    # # Temporary fix to cases where no coref was found
    if ind > 0:
        return NP_List[ind - 1]
    else:
        return NP_List[ind + 1]


def get_number(POS):
    """ returns singular, plural, or 'None' for a given POS.
    """
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

    if POS in numberDict:
        return numberDict[POS]
    else:
        return None


def get_gender(string):
    # Check for gender agreement

    labeled_names = (
        [(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
    random.shuffle(labeled_names)

    def gender_features(word):
        return {'last_letter': word[-1]}

    featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
    train_set, test_set = featuresets[500:], featuresets[:500]
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    return classifier.classify(gender_features(string))


# TODO(sam): move to utils
def generate_coref_id():
  key = ''.join(random.choice('ABCDEF0123456789') for i in range(5))
  return key


# TODO(sam): move to utils
def insert_coref_tag(data, coref_id, ref):
    tag = '<COREF ID="%s"' % coref_id
    # find coref in original text
    pos_in_text = data.find(tag) + len(tag)
    # smash the new reference id into the original file data
    data = '%s REF="%s"%s' % (data[:pos_in_text], ref['id'], data[pos_in_text:])
    return data


def add_np_coref_tags(data):
    # convert data to proper xml object to easily exact the pure text from data
    xml_data = ET.fromstring(data)
    pure_text = ET.tostring(xml_data, encoding='utf8', method='text')

    # get sentences
    sentences = sent_tokenize(pure_text)

    # add pos tags to all tokens per sentence
    tagged_sentences = []
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        tagged_sentences.append(nltk.pos_tag(tokens))

    # TODO: find a good grammar to parse the sentences into tree structures
    # http://www.nltk.org/book/ch07.html
    grammar = "NP: {<DT>?<JJ>*<NN>+ |\
               <DT><NN><NN>. |\
               <IN><CD><NNS> |\
               <IN><CD><NN> |\
               <DT><NN> |\
               <NNP>+<POS>*<NN>*}"
    cp = nltk.RegexpParser(grammar)

    # parse each of the tagged sentences into recursive tree structures
    treed_sentences = []
    for tagged_sentence in tagged_sentences:
        treed_sentences.append(cp.parse(tagged_sentence))

    # builds the full, corefed and tagged data string back up while tearing
    # down the existing data string
    corefed_data = ""

    # tears down the existing data string while adding coref tags to all nps
    for parse in treed_sentences:
        for subtree in parse.subtrees(filter=lambda t: t.label() == 'NP'):
            # builds up the noun phrase from the flattened subtree
            constituents = [constituent[0] for constituent in subtree.flatten()]
            noun_phrase = " ".join(constituents)

            # finds the position to smash the tag into the data string
            beg_pos_in_data = data.find(noun_phrase)
            if beg_pos_in_data == -1:
                # the noun phrase wasn't found (probably a problem with new lines)
                continue

            end_pos_in_data = beg_pos_in_data + len(noun_phrase)
            if "COREF" in data[beg_pos_in_data:end_pos_in_data]:
                # the noun phrase has likely already been marked with coref tag
                continue

            if len(data) > end_pos_in_data + 8 and \
               "</COREF>" in data[beg_pos_in_data:end_pos_in_data + 8]:
                # the noun phrase has likely already been marked with coref tag
                continue

            if beg_pos_in_data > 16 and \
               "<COREF ID=" in data[beg_pos_in_data - 16:end_pos_in_data]:
                # the noun phrase has likely already been marked with coref tag
                continue

            prev_data = corefed_data + data[:beg_pos_in_data]
            new_coref_id = generate_coref_id()

            # smashes a new coreference tag into the data text
            corefed_data = "%s<COREF ID=\"%s\">%s</COREF>" % (prev_data, new_coref_id, noun_phrase)
            data = data[end_pos_in_data:]

    if len(data) > 0:
      corefed_data = corefed_data + data

    return corefed_data


# main "method" that kicks off various routines
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "expected usage:\n\tpython coreference.py <list_file> <response_dir>"
        exit(1)

    # open files
    file_list = open(sys.argv[1], 'r')

    # for each file, run the coreference algorithm:
    for filename in file_list:
        infile = filename.strip()
        data = open(infile, 'r').read() # raw original file data

        # do pos tagging to figure out which other words likely need the xml
        # coreference tags. adds xml coref tags to all noun phrases
        data = add_np_coref_tags(data) # drops accuracy down to 17%

        # gets just the xml'd/pre-labeled coreference tokens
        anaphors = ET.fromstring(data) # just the xml'd bits of the text

        # build list of all anaphors
        anaphorList = []

        for anaphor in anaphors:
            tokens = nltk.word_tokenize(anaphor.text)
            tagged = nltk.pos_tag(tokens)

            # build element to hold all relevant information about anaphora
            anaphorList.append({
                'id': anaphor.attrib['ID'],
                'text': anaphor.text,
                'POS': tagged,
                'number': get_number(tagged[-1][1]),
                'gender': get_gender(anaphor.text[-1]),
                })

        for ind, anaphor in enumerate(anaphorList):
            # finds the coreference to 
            coref = find_coref(ind, anaphor, anaphorList)
            if len(anaphor['id']) < 4: #only insert corefs for the original anaphora
                data = insert_coref_tag(data, anaphor['id'], coref)
#
        # get just the input filename to build the corresponding output file path
        infile = infile.split('.')[0].split('/')[-1]
        outfile = sys.argv[2] + '/' + infile + '.response'

        # print outfile
        with open(outfile, "w") as text_file:
            text_file.write(data)

    file_list.close()
