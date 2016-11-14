#!/usr/bin/python2.7

import coreference
import utils
import nltk
import sys


# main "method" that kicks off various routines
if __name__ == "__main__":
    try:
      # attempt to use a thing
      nltk.word_tokenize("test")
    except LookupError:
      # if it's not already downloaded, download everything
      nltk.download('punkt')
      nltk.download('maxent_ne_chunker')
      nltk.download('words')
      nltk.download('averaged_perceptron_tagger')
      nltk.download('wordnet')
      nltk.download('names')

    if not len(sys.argv) == 3:
        print "expected usage:\n\tpython coreference.py <list_file> <response_dir>"
        exit(1)

    # open files
    file_handler = open(sys.argv[1], 'r')
    file_list = map(lambda filename: filename.strip(), file_handler.readlines())
    file_handler.close()

    outfile = sys.argv[2]
    print "Processing:\n\t%s\nInto: %s" % ("\n\t".join(file_list), outfile)

    responselist_file_name = "data/filelists/responselist.txt"
    responsefile = open(responselist_file_name, "w")
    for filename in file_list:
      responsefilename = utils.build_new_file_path(filename, "responses")
      responsefile.write(responsefilename + "\n")
    responsefile.close()

    coreference.process_files(file_list, outfile)

    print "\nDone coreference tagging! Response file list: %s" % responselist_file_name
