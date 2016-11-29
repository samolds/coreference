#!/usr/bin/python2.7

from nltk.tokenize import sent_tokenize, word_tokenize
from difflib import SequenceMatcher as editDifference
import xml.etree.ElementTree as ET
from datetime import datetime
import utils
import nltk
from lib.hobbs import hobbs
from lib.stat_parser.parser import Parser as CkyStatParser
from nltk.corpus import wordnet as wn

print wn.synsets('IBM')

# finds coreference from within a list of possible noun phrases
# returns an id of the tagged coref noun phrase or `None` if nothing was found
def find_coref(anaphor_idx, np_list, sentence_trees):
    anaphor = np_list[anaphor_idx]

    # only consider anaphors/NPs that show up before the current one
    prior_anaphor_indices = range(anaphor_idx - 1, -1, -1)

    #Match Named Entities
    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

        # same category of NE
        if anaphor['NE'] is not None and anaphor['NE'] == coref['NE'] :
            # strings are very similar
            if editDifference(None, anaphor['text'], coref['text']).ratio() > 0.65:
                # print anaphor['NE'], '--', anaphor['text'], '--', coref['text']
                return coref


    # look for any noun phrases with exact string match or just head noun
    # string match in prior anaphors
    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

        # exact string match or just the head nouns match
        if anaphor['text'] == coref['text'] or \
            anaphor['text'].split()[-1] == coref['text'].split()[-1]:
            return coref

        # strings are very similar
        if editDifference(None, anaphor['text'], coref['text']).ratio() > 0.65:
            return coref

    for prior_anaphor_idx in prior_anaphor_indices:
        coref = np_list[prior_anaphor_idx]

    #look for synonyms

        w1 = wn.synsets(anaphor['text'].split()[-1], pos=wn.NOUN)
        w2 = wn.synsets(coref['text'].split()[-1], pos=wn.NOUN)
        #
        # print
        if w1 and w2:
            if(w1[0].wup_similarity(w2[0])) > .65:
                return coref


    ## No string matching was found, search again, this time with pronoun
    ## resolution
    #pronouns = ["He", "he", "Him", "him", "She", "she", "Her",
    #            "her", "It", "it", "They", "they"]
    #reflexives = ["Himself", "himself", "Herself", "herself",
    #              "Itself", "itself", "Themselves", "themselves"]
    #pro = anaphor['text']
    #if pro in pronouns or pro in reflexives:
    #    # search through all sentence trees until we find the one the pronoun
    #    # is in
    #    sents = []
    #    while len(sents) < len(sentence_trees):
    #        full_sents = sentence_trees[:len(sents) + 1]
    #        sents = [full_sent['parsed'] for full_sent in full_sents]
    #        xml_id = "ID=\"%s\"" % anaphor['id']
    #        if xml_id in full_sents[-1]['raw']:
    #            node = anaphor['pos'][-1]
    #            loc_in_tree = hobbs.get_pos(sents[-1], node)
    #            loc_in_tree = loc_in_tree[:-1]
    #            break

    #    noun_phrase = ""
    #    tree = None
    #    pos = None
    #    if pro in pronouns:
    #        tree, pos = hobbs.hobbs(sents, loc_in_tree)
    #    elif pro in reflexives:
    #        tree, pos = hobbs.resolve_reflexive(sents, loc_in_tree)

    #    if tree and pos:
    #        if type(tree[pos]) == nltk.tree.Tree:
    #            noun_phrase = " ".join(map(lambda np: np[0], tree[pos].pos()))
    #        else:
    #            noun_phrase = tree[pos]

    #    for coref in np_list:
    #        if coref['text'] == noun_phrase:
    #            print anaphor, coref
    #            return coref


    # No prior resolution was found, search again, this time with named entity
    # resolution
    #TODO: include named entity resolution



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

    ## ------------------------------------------------------------------------
    #treed_sentences = []
    #for idx, sentence in enumerate(sentences):
    #    sentence_tree = cky_stat_parser.nltk_parse(sentence)
    #    treed_sentences.append({
    #      "raw": raw_sentences[idx],
    #      "parsed": sentence_tree,
    #    })

    ## ------------------------------------------------------------------------
    # add pos tags to all tokens per sentence
    tagged_sentences = []
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        tagged_sentences.append(nltk.pos_tag(tokens))

    # TODO: find a good grammar to parse the sentences into tree structures
    # http://www.nltk.org/book/ch07.html
    #grammar = "NP: {<DT>?<JJ>*<NN>+ |\
    #           <DT><NN><NN>. |\
    #           <IN><CD><NNS> |\
    #           <IN><CD><NN> |\
    #           <DT><NN> |\
    #           <NNP>+<POS>*<NN>*}"
    grammar = r"""
        NP: {<DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
        PP: {<IN><NP>}               # Chunk prepositions followed by NP
        VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
        CLAUSE: {<NP><VP>}           # Chunk NP, VP
        """
    cp = nltk.RegexpParser(grammar)

    # chunked_sentences = nltk.ne_chunk_sents(tagged_sentences)
    # entity_names = []
    # for sentence in chunked_sentences:
    #     # Print results per sentence
    #     # print extract_entity_names(sentence)
    #
    #     entity_names.extend(extract_entity_names(sentence))
    #
    # # Print all entity names
    # # print entity_names
    #
    # # Print unique entity names
    # # print set(entity_names)



    # parse each of the tagged sentences into recursive tree structures
    treed_sentences = []
    for idx, tagged_sentence in enumerate(tagged_sentences):
        sentence_tree = cp.parse(tagged_sentence)

        treed_sentences.append({
          "raw": raw_sentences[idx],
          "parsed": sentence_tree,
        })
    ## ------------------------------------------------------------------------

    # builds the full, corefed and tagged data string back up while tearing
    # down the existing data string
    corefed_data = ""

    # tears down the existing data string while adding coref tags to all nps
    for parse in treed_sentences:
        parse = parse['parsed']
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

            if utils.nested_noun_phrase(data, beg_pos_in_data):
                continue

            prev_data = corefed_data + data[:beg_pos_in_data]
            new_coref_id = utils.generate_coref_id(6) # 6 characters long

            # smashes a new coreference tag into the data text
            corefed_data = "%s<COREF ID=\"%s\">%s</COREF>" % (prev_data,
                           new_coref_id, noun_phrase)
            data = data[end_pos_in_data:]

    if len(data) > 0:
        corefed_data = corefed_data + data

    return corefed_data, treed_sentences



# for each file, run the coreference algorithm:
def process_files(file_list, out_file):
    start_time = datetime.now()
    cky_stat_parser = CkyStatParser() # initialize sentence tagger/parser
    for filename in file_list:
        print "\tprocessing %s..." % filename
        file_handler = open(filename, 'r')
        data = file_handler.read() # raw original file data
        file_handler.close()

        # do pos tagging to figure out which other words likely need the xml
        # coreference tags. adds xml coref tags to all noun phrases
        data, sentence_trees = add_np_coref_tags(data, cky_stat_parser)

        # gets just the xml'd/pre-labeled coreference tokens
        #try:
        anaphors = ET.fromstring(data) # just the xml'd bits of the text
        #except ET.ParseError:
        #  import pdb; pdb.set_trace()

        # build list of all anaphors
        anaphor_list = []

        for anaphor in anaphors:
            # TODO: just reuse the tagging done by add_np_coref_tags
            #tokens = word_tokenize(anaphor.text)
            #tagged = nltk.pos_tag(tokens)
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
                'pos': tagged.pos()[-1][1],
                'plurality': utils.get_plurality(tagged.pos()[-1][1]),
                # 'plurality': utils.get_plurality(tagged[-1]),
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

    end_time = datetime.now()
    time_diff = (end_time - start_time).total_seconds()
    print "ran for %0.3f seconds (%0.3f minutes)!" % (time_diff, time_diff / 60.0)
