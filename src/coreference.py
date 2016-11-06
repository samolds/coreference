#!/usr/bin/python2.7

from nltk.tokenize import sent_tokenize, word_tokenize
import sys
import xml.etree.ElementTree as ET
import nltk
import os

nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('names')


# main "method" that kicks off various routines
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "expected usage:\n\tpython main.py <list_file> <response_dir>"
        exit(1)

    # open files
    files = open(sys.argv[1],'r')

    #For each one, run the coreference algorithm:
    for line in files:
        infile = line.replace('\n', ' ').replace('\r', '').strip()
        file = open(infile, 'r')
        data = file.read()
        anaphors = ET.fromstring(data)
        pureText = ET.tostring(anaphors, encoding='utf8', method='text')

        # Check for gender agreement

        from nltk.corpus import names

        labeled_names = (
        [(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
        import random

        random.shuffle(labeled_names)


        def gender_features(word):
            return {'last_letter': word[-1]}


        featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
        train_set, test_set = featuresets[500:], featuresets[:500]
        classifier = nltk.NaiveBayesClassifier.train(train_set)

        # Check for number agreement

        numberAgreement = {"NN": "singular",
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

        anaphorList = []
        for anaphor in anaphors:
            tokens = nltk.word_tokenize(anaphor.text)
            tagged = nltk.pos_tag(tokens)

            number = tagged[-1][1]
            if number in numberAgreement:
                number = numberAgreement[tagged[- 1][1]]
            else:
                number = None

            el = {'id': anaphor.attrib['ID'], 'text': anaphor.text, 'POS':tagged, 'number': number, \
                  'gender': classifier.classify(gender_features(anaphor.text[- 1]))}
            # print el
            anaphorList.append(el)


        def find_coref(ind, anaphor, anaphorList):  # Fist attempt at coreferencing based on gender, number agreement, and string matching
            # Only consider anaphors/NPs that show up before the current one

            for el in list(reversed(range(ind - 2))):
                coref = anaphorList[el]
                if anaphor['text'] == coref['text'] or anaphor['text'].split()[-1] in coref[
                    'text']:  # String Matching - entire NP or head noun
                    # print 'anaphor:', anaphor['text'].split(), '   coref: ', coref['text'].split()
                    return coref
                elif anaphor['gender'] == coref['gender'] and anaphor['number'] == coref[
                    'number']:  # check for gender and number, or string agreement
                    # print 'anaphor:', anaphor['text'], '   coref: ', coref['text']
                    return coref

            if ind > 0:
                return anaphorList[ind-1]
            else:
                return anaphorList[ind + 1]


        for ind, anaphor in enumerate(anaphorList):
            coref = find_coref(ind, anaphor, anaphorList)
            #Find coref in original text:
            string = '<COREF ID="' + anaphor['id'] + '"'
            posInText = data.find(string) + len(string)
            print ('found at ', posInText)
            data = data[:posInText] + ' REF="'+coref['id'] + '"'+ data[posInText:]
        print data


        crf_file, crf_path = os.path.splitext(sys.argv[1])
        out_file, out_path = os.path.splitext(sys.argv[2])

        infile = infile.split('.')[0].split('/')[-1]
        outfile = sys.argv[2]+'/' + infile + '.response'
        print outfile
        with open(outfile, "w") as text_file:
            text_file.write("%s" %data)

        # Splitting Sentences
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

        # close files
        file.close()


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
