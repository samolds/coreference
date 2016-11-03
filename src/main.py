#!/usr/bin/python2.7

from nltk.tokenize import TreebankWordTokenizer
import sys


if __name__ == "__main__":
  s = '''Good muffins cost $3.88\nin New York.  
  Please buy me\ntwo of them.\nThanks.'''
  x = TreebankWordTokenizer().tokenize(s)
  print "\theyo %s\n\t%s" % (" ".join(sys.argv[1:]), x)
