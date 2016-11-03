#!/usr/bin/python2.7

from nltk.tokenize import TreebankWordTokenizer
import sys


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
  if not len(sys.argv) == 2:
    print "expected usage:\n\tpython main.py <input file>"
    exit(1)

  # open files
  data_file = open(sys.argv[1], 'r')

  # build structures from corresponding input files
  tokens_by_line = build(data_file)
  for tokens in tokens_by_line:
    print ":".join(tokens)

  # close files
  data_file.close()
