#!/usr/bin/python2.7

from nltk.tokenize import sent_tokenize, word_tokenize
from difflib import SequenceMatcher as editDifference
import xml.etree.ElementTree as ET
import utils
import nltk


# Function that actually finds the coreference from within a list of possible NPs
def find_coref(ind, anaphor, NP_List):
    # Fist attempt at coreferencing based on gender, number agreement, and
    # string matching
    # Only consider anaphors/NPs that show up before the current one
    for el in list(reversed(range(ind))):
        coref = NP_List[el]

        if anaphor['text'] == coref['text'] or \
            anaphor['text'].split()[-1] in coref or \
            anaphor['text'].split()[0] in coref['text']:
            # String Matching - entire NP or head noun
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

            if utils.nested_noun_phrase(data, beg_pos_in_data):
                continue

            prev_data = corefed_data + data[:beg_pos_in_data]
            new_coref_id = utils.generate_coref_id()

            # smashes a new coreference tag into the data text
            corefed_data = "%s<COREF ID=\"%s\">%s</COREF>" % (prev_data,
                           new_coref_id, noun_phrase)
            data = data[end_pos_in_data:]

    if len(data) > 0:
        corefed_data = corefed_data + data

    return corefed_data



# for each file, run the coreference algorithm:
def process_files(file_list, out_file):
    for filename in file_list:
        file_handler = open(filename, 'r')
        data = file_handler.read() # raw original file data
        file_handler.close()

        # do pos tagging to figure out which other words likely need the xml
        # coreference tags. adds xml coref tags to all noun phrases
        data = add_np_coref_tags(data)

        # gets just the xml'd/pre-labeled coreference tokens
        anaphors = ET.fromstring(data) # just the xml'd bits of the text

        # build list of all anaphors
        anaphorList = []

        for anaphor in anaphors:
            tokens = word_tokenize(anaphor.text)
            tagged = nltk.pos_tag(tokens)

            # build element to hold all relevant information about anaphora
            anaphorList.append({
                'id': anaphor.attrib['ID'],
                'text': anaphor.text,
                'POS': tagged,
                'number': utils.get_number(tagged[-1][1]),
                'gender': utils.get_gender(anaphor.text[-1]),
                })

        for ind, anaphor in enumerate(anaphorList):
            # finds the coreference to 
            coref = find_coref(ind, anaphor, anaphorList)
            if len(anaphor['id']) < 4:
                # only insert corefs for the original anaphora
                data = utils.insert_coref_tag(data, anaphor['id'], coref)

        outfile = utils.build_new_file_path(filename, out_file)

        # print outfile
        with open(outfile, "w") as text_file:
            text_file.write(data)
