#!/usr/bin/python2.7

from nltk.tokenize import sent_tokenize, word_tokenize
import sys
import xml.etree.ElementTree as ET
import nltk
import os
import random
import string


# Uncomment for first run!
# nltk.download('punkt')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('names')

# Function that actually finds the coreference from within a list of possible NPs
def find_coref(ind, anaphor,
               NP_List):  # Fist attempt at coreferencing based on gender, number agreement, and string matching
    # Only consider anaphors/NPs that show up before the current one
    for el in list(reversed(range(ind - 2))):
        coref = NP_List[el]
        if anaphor['text'] == coref['text'] or anaphor['text'].split()[-1] in coref[
            'text']:  # String Matching - entire NP or head noun
            return coref
        elif anaphor['gender'] == coref['gender'] and anaphor['number'] == coref[
            'number']:  # check for gender and number, or string agreement
            return coref

    # Temporary fix to cases where no coref was found
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

    from nltk.corpus import names


    labeled_names = (
        [(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
    random.shuffle(labeled_names)

    def gender_features(word):
        return {'last_letter': word[-1]}

    featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
    train_set, test_set = featuresets[500:], featuresets[:500]
    classifier = nltk.NaiveBayesClassifier.train(train_set)

    return classifier.classify(gender_features(string))

# main "method" that kicks off various routines
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "expected usage:\n\tpython main.py <list_file> <response_dir>"
        exit(1)

    # open files
    files = open(sys.argv[1], 'r')

    # For each file, run the coreference algorithm:
    for file in files:
        infile = file.replace('\n', ' ').replace('\r', '').strip()
        data = open(infile, 'r').read()

        #Strip XML
        anaphors = ET.fromstring(data)

        anaphorList = []
        for anaphor in anaphors:
            tokens = nltk.word_tokenize(anaphor.text)
            tagged = nltk.pos_tag(tokens)

            el = {'id': anaphor.attrib['ID'], 'text': anaphor.text, 'POS': tagged, 'number': get_number(tagged[-1][1]), \
                  'gender': get_gender(anaphor.text.strip()[- 1])}

            anaphorList.append(el)



        for ind, anaphor in enumerate(anaphorList):
            coref = find_coref(ind, anaphor, anaphorList)

            # Find coref in original text:
            searchString = '<COREF ID="' + anaphor['id'] + '"'
            posInText = data.find(searchString) + len(searchString)
            data = data[:posInText] + ' REF="' + coref['id'] + '"' + data[posInText:]

        crf_file, crf_path = os.path.splitext(sys.argv[1])
        out_file, out_path = os.path.splitext(sys.argv[2])

        infile = infile.split('.')[0].split('/')[-1]
        outfile = sys.argv[2] + '/' + infile + '.response'

        # print outfile
        with open(outfile, "w") as text_file:
            text_file.write("%s" % data)


        ## Not currently being used for the algorithm!!

        # Splitting Sentences
        pureText = ET.tostring(anaphors, encoding='utf8', method='text')
        allSentences = sent_tokenize(pureText)

        # POS tagging
        tagged = []

        for sentence in allSentences:
            tokens = nltk.word_tokenize(sentence)
            tagged.append(nltk.pos_tag(tokens))

        # TO DO: find a good grammer to parse the sentences already tagged with POS

        grammar = "NP: {<DT>?<JJ>*<NN>+ | <DT><NN><NN>. | <IN><CD><NNS> | <IN><CD><NN> | <DT><NN> | <NNP>+<POS>*<NN>*}"

        cp = nltk.RegexpParser(grammar)

        parsed = [];
        for taggedSentence in tagged:
            parsed.append(cp.parse(taggedSentence))

        for parse in parsed:
            for subtree in parse.subtrees(filter=lambda t: t.label() == 'NP'):
                # el = {'id': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)), \
                #       'text': subst.text, 'POS': subtree.leaves(),
                #       'number': get_number(subtree.leaves()[-1][1]), \
                #       'gender': get_gender(subtree.text[- 1])}
                print(subtree.leaves())

        # close files
        # file.close()


        # parsed.draw()
        #  entities = nltk.chunk.ne_chunk(tagged)

        # for pos in parsed.treepositions():
        #   print parsed[pos]
        # for subtree in parsed.subtrees():
        #   print(subtree)

        # for subtree in parsed.subtrees(filter=lambda t: t.label() == 'NP'):
        #   print(subtree)

        # print("tagged = %s") % (tagged)
        # print("entities = %s") % (entities)
        # print("parsed = %s") % (parsed)
