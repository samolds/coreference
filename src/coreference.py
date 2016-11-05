#!/usr/bin/python2.7

from nltk.tokenize import TreebankWordTokenizer, sent_tokenize, word_tokenize
import sys
import xml.etree.ElementTree as ET
import nltk
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')
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

  # for anaphor in anaphors:
  #   print anaphor.attrib, anaphor.text

  #Sentence splitter
  # tokens = TreebankWordTokenizer().tokenize(data_file.read())

  allSentences = sent_tokenize(pureText)
  # for ind, el in enumerate(allSentences):
  #   print ind, el
  # filt = [x for x in allSentences if 'ID="3"' in x]
  # print filt

  grammar = "NP: {<DT>?<JJ>*<NN>}"

  sentence = allSentences[4]

  tokens = nltk.word_tokenize(sentence)
  tagged = nltk.pos_tag(tokens)
  cp = nltk.RegexpParser(grammar)
  parsed = cp.parse(tagged)
  entities = nltk.chunk.ne_chunk(tagged)

  print("tagged = %s") % (tagged)
  print("entities = %s") % (entities)
  print("parsed = %s") % (parsed)



  # print text

  # build structures from corresponding input files
  # tokens_by_line = build(data_file)
  # for tokens in tokens_by_line:
    # print ":".join(tokens)

  # close files
  file.close()
