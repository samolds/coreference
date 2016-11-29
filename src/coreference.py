#!/usr/bin/python2.7

from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet as wn
import nltk

from difflib import SequenceMatcher as editDifference
import xml.etree.ElementTree as ET
from datetime import datetime
import multiprocessing

from lib.stat_parser.parser import Parser as CkyStatParser
import utils
import hobbs


# setting DEBUG to false will cause all of the file processing to happen
# concurrently. faster, but harder to debug
DEBUG = False

# finds coreference from within a list of possible noun phrases
# returns an id of the tagged coref noun phrase or `None` if nothing was found
def find_coref(anaphor_idx, np_list, sentence_trees):
    anaphor = np_list[anaphor_idx]

    # only consider anaphors/NPs that show up before the current one
    prior_anaphor_indices = range(anaphor_idx - 1, -1, -1)

    # Match Named Entities
    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

        # same category of NE
        if anaphor['NE'] is not None and anaphor['NE'] == coref['NE']:
            # strings are very similar
            if editDifference(None, anaphor['text'], coref['text']).ratio() > 0.65:
                return coref


    # look for any noun phrases with exact string match or just head noun
    # string match in prior anaphors
    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

        # exact string match or just the head nouns match
        if anaphor['text'] == coref['text'] or anaphor['text'].split()[-1] == coref['text'].split()[-1] or \
                        anaphor['text'].split()[-1] in coref['text']:
            return coref

        # strings are very similar
        if editDifference(None, anaphor['text'], coref['text']).ratio() > 0.65:
            return coref

    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

        # look for synonyms
        w1 = wn.synsets(anaphor['text'].split()[-1], pos=wn.NOUN)
        w2 = wn.synsets(coref['text'].split()[-1], pos=wn.NOUN)
        if w1 and w2:
            if(w1[0].wup_similarity(w2[0])) > .65:
                return coref


    ## -------------------------- TODO ----------------------------------------
    # No string matching was found, search again, this time with pronoun
    # resolution
    pro = anaphor['text']
    if pro in utils.PRONOUNS or pro in utils.REFLEXIVES:
        # search through all sentence trees until we find the one the pronoun
        # is in
        pre_pronoun_trees = []
        while len(pre_pronoun_trees) < len(sentence_trees):
            full_sents = sentence_trees[:len(pre_pronoun_trees) + 1]
            pre_pronoun_trees = [full_sent['parsed'] for full_sent in full_sents]
            xml_id = "ID=\"%s\"" % anaphor['id']
            if xml_id in full_sents[-1]['raw']:
                break

        node = anaphor['pos'][-1]
        loc_in_tree = hobbs.get_tree_position(pre_pronoun_trees[-1], node)

        coref = None
        if pro in utils.PRONOUNS:
            coref = hobbs.hobbs(pre_pronoun_trees, loc_in_tree, anaphor, np_list)
        elif pro in utils.REFLEXIVES:
            coref = hobbs.hobbs_reflexive(pre_pronoun_trees, loc_in_tree, anaphor, np_list)
        
        if coref:
            return coref
    ## ------------------------------------------------------------------------

    # No prior resolution was found, search again, this time with gender and number
    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

        # check for gender and number, or string agreement
        if anaphor['gender'] == coref['gender'] and \
            anaphor['plurality'] == coref['plurality']:
            return coref

    # didn't find any coreferences
    return None


def add_np_coref_tags(data, cky_stat_parser):
    # convert data to proper xml object to easily exact the pure text from data
    xml_data = ET.fromstring(data)
    pure_text = ET.tostring(xml_data, encoding='utf8', method='text')

    # get sentences
    raw_sentences = sent_tokenize(data)
    sentences = sent_tokenize(pure_text)

    # parse each of the sentences into tagged recursive tree structures
    treed_sentences = []
    for idx, sentence in enumerate(sentences):
        # NOTE: this cky_stat_parser takes a long time to tag :(
        sentence_tree = cky_stat_parser.nltk_parse(sentence)
        treed_sentences.append({
          "raw": raw_sentences[idx],
          "parsed": sentence_tree,
        })

    # just smashes coref xml tags into the data. because the subtrees don't
    # always find nps from left to right, we simply just look for the first
    # string match from left to right to tag. this is acceptable because the
    # first time that string appears is probably the one we want to refer to
    for parse in treed_sentences:
        parse = parse['parsed']
        for subtree in parse.subtrees(filter=lambda t: t.height() < 4 and \
                       (t.label() == 'NP' or t.label() == 'NNP')):
            # builds up the noun phrase from the flattened subtree
            constituents = [constituent for constituent in subtree.flatten()]
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

            if utils.nested_noun_phrase(data, beg_pos_in_data):
                continue

            new_coref_id = utils.generate_coref_id(6) # 6 characters long

            # smashes a new coreference tag into the data text
            data = "%s<COREF ID=\"%s\">%s</COREF>%s" % (data[:beg_pos_in_data],
                   new_coref_id, noun_phrase, data[end_pos_in_data:])

    return data, treed_sentences



def coreference(filename, out_file, cky_stat_parser):
    file_handler = open(filename, 'r')
    data = file_handler.read() # raw original file data
    file_handler.close()

    # do pos tagging to figure out which other words likely need the xml
    # coreference tags. adds xml coref tags to all noun phrases
    data, sentence_trees = add_np_coref_tags(data, cky_stat_parser)

    # gets just the xml'd/pre-labeled coreference tokens
    anaphors = ET.fromstring(data) # just the xml'd bits of the text

    # build list of all anaphors
    anaphor_list = []

    for anaphor in anaphors:
        # TODO: just reuse the tagging done by add_np_coref_tags
        tagged = cky_stat_parser.nltk_parse(anaphor.text)

        NE = utils.extract_entity_names(nltk.ne_chunk(tagged.pos()))
        LABELS = utils.extract_entity_labels(nltk.ne_chunk(tagged.pos()))
        if NE:
            namedEntity = LABELS[-1]
        else:
            namedEntity = None

        # build element to hold all relevant information about anaphora
        anaphor_list.append({
            'id': anaphor.attrib['ID'],
            'text': anaphor.text,
            'pos': tagged,
            'plurality': utils.get_plurality(tagged.pos()[-1][1]),
            'gender': utils.get_gender(anaphor.text),
            'NE': namedEntity
        })

    for idx, anaphor in enumerate(anaphor_list):
        # only care about the nps with short ids
        if len(anaphor['id']) < 4:
            # finds the coreference to the anaphor
            coref = find_coref(idx, anaphor_list, sentence_trees)
            if coref: # find coref returns an anaphor id or `None`
                # only insert corefs for the original anaphora
                data = utils.insert_coref_tag(data, anaphor['id'], coref)

    outfile = utils.build_new_file_path(filename, out_file)

    # print outfile
    with open(outfile, "w") as text_file:
        text_file.write(data)


# for each file, run the coreference algorithm:
def process_files(file_list, out_file):
    start_time = datetime.now()
    cky_stat_parser = CkyStatParser() # initialize sentence tagger/parser
    if DEBUG:
        print "== This will probably take about %0.f minutes ==" \
              % (len(file_list) * 2.0)
        # process each data file one at a time
        for filename in file_list:
            print "\tprocessing %s..." % filename
            coreference(filename, out_file, cky_stat_parser)
    else:
        print "== This will probably take about %0.f minutes ==" \
              % (len(file_list) / 1.5)
        # process each data file concurrently
        processes = [{"process": multiprocessing.Process(target=coreference,
                                 args=(filename, out_file, cky_stat_parser)),
                      "filename": filename}
                     for filename in file_list]

        for p in processes:
          print "\tprocessing %s concurrently..." % p['filename']
          p['process'].start()

        for p in processes:
          p['process'].join()


    end_time = datetime.now()
    time_diff = (end_time - start_time).total_seconds()
    print "ran for %0.3f seconds (%0.3f minutes)!" % (time_diff, time_diff / 60.0)
