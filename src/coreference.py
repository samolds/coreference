#!/usr/bin/python2.7

from nltk.tokenize import TreebankWordTokenizer, sent_tokenize, word_tokenize
import sys
import xml.etree.ElementTree as ET
import nltk

import hobbs


nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('names')
# builds a list of tokens by each line
# param:  data_file: file handler
# return: list of list of tokens
def build(data_file):
  tokens_by_line = []
  for line in data_file:
    tokens = TreebankWordTokenizer().tokenize(line)
    if len(tokens) > 0:
      tokens_by_line.append(tokens)
  return tokens_by_line


# main "method" that kicks off various routines
if __name__ == "__main__":
  if not len(sys.argv) == 3:
    print "expected usage:\n\tpython main.py <input file> <response_dir>"
    exit(1)

  # open files
  file = open(sys.argv[1], 'r')
  data = file.read()
  anaphors = ET.fromstring(data)
  pureText = ET.tostring(anaphors, encoding='utf8', method='text')


#Check for gender agreement

  from nltk.corpus import names
  labeled_names = ([(name, 'male') for name in names.words('male.txt')] + [(name, 'female') for name in names.words('female.txt')])
  import random
  random.shuffle(labeled_names)


  def gender_features(word):
    return {'last_letter': word[-1]}

  featuresets = [(gender_features(n), gender) for (n, gender) in labeled_names]
  train_set, test_set = featuresets[500:], featuresets[:500]
  classifier = nltk.NaiveBayesClassifier.train(train_set)


#Check for number agreement

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

    number = tagged[len(tagged)-1][1]
    if number in numberAgreement:
      number = numberAgreement[tagged[len(tagged)-1][1]]
    else:
      number = None

    el = {'id': anaphor.attrib['ID'], 'text': anaphor.text, 'number': number, \
          'sex': classifier.classify(gender_features(anaphor.text[len(anaphor.text)-1]))}
    print el
    anaphorList.append(el)

  allSentences = sent_tokenize(pureText)
  # for ind, el in enumerate(allSentences):
  #   print ind, el
  # filt = [x for x in allSentences if 'ID="3"' in x]
  # print filt

  grammar = "NP: {<DT>?<JJ>*<NN>+ | <DT><NN><NN>. | <IN><CD><NNS> | <IN><CD><NN> | <DT><NN> | <NNP>+<POS>*<NN>*}"

  sentence = allSentences[5]

  tokens = nltk.word_tokenize(sentence)
  tagged = nltk.pos_tag(tokens)
  cp = nltk.RegexpParser(grammar)
  parsed = cp.parse(tagged)

  # parsed.draw()
#  entities = nltk.chunk.ne_chunk(tagged)

  print sentence

  # for pos in parsed.treepositions():
  #   print parsed[pos]
  # for subtree in parsed.subtrees():
  #   print(subtree)

  # for subtree in parsed.subtrees(filter=lambda t: t.label() == 'NP'):
  #   print(subtree)

  # print("tagged = %s") % (tagged)
  # print("entities = %s") % (entities)
  # print("parsed = %s") % (parsed)


  # close files
  file.close()
