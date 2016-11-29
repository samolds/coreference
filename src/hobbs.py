#!/usr/bin/python2.7

from difflib import SequenceMatcher as editDifference
from nltk.corpus import names
import nltk


def dirty(sentence_trees, node_position, anaphor, np_list):
  # 1. Begin at the NP node immediately dominating the pronoun
  sentence_trees.reverse() # flip it around so the most recent is at the head
  pronoun_sentence_tree = sentence_trees[0] # pronoun expected to be in last tree
  dominant_np_position = node_position[:-1]  # strip away last index for parent
  dom_np_tree = pronoun_sentence_tree[dominant_np_position]

  # 2. Go up the tree to the first NP or S node encountered. Call this node X
  #    and the path used to reach it p.
  search_position = dominant_np_position
  path = [search_position]
  while search_position:
    search_position = search_position[:-1] # strip away last index for parent
    path.append(search_position)
    if pronoun_sentence_tree[search_position].label() == "S" or \
       "NP" in pronoun_sentence_tree[search_position].label():
      break
  x = pronoun_sentence_tree[search_position]

  # 3. Traverse all branches below node X to the left of path p in a
  #    left-to-right, breadth-first fashion. Propose as an antecedent any NP
  #    node that is encountered which has an NP or S node between it and X.
  for branch_pos in x.treepositions():
    if branch_pos >= path[0]:
      continue
    branch = x[branch_pos]
    if type(branch) != nltk.tree.Tree:
      continue
    if branch.label() == "NP":
      return resolve(x, branch_pos, anaphor, np_list)

  # 4. If node X is the highest S node in the sentence, traverse the surface
  #    parse trees of previous sentences in the text in order of recency, the
  #    most recent first; each tree is traversed in a left-to-right,
  #    breadth-first manner, and when an NP node is encountered, it is proposed
  #    as an antecedent. If X is not the highest S node in the sentence,
  #    continue to step 5.
  if x == pronoun_sentence_tree:
    for tree in sentence_trees:
      for branch_pos in tree.treepositions():
        branch = tree[branch_pos]
        if type(branch) != nltk.tree.Tree:
          continue
        if branch.label() == "NP":
          return resolve(x, branch_pos, anaphor, np_list)

  # TODO: Step 5, 6, 7, 8, 9

  return None


# returns a coref object from the np_list given the chosen noun phrase from
# hobbs algorithm
def resolve(sentence_tree, guess_position, anaphor, np_list):
  guess = sentence_tree[guess_position]
  if type(guess) == nltk.tree.Tree:
    guess = " ".join(map(lambda np: np[0], guess.pos()))

  # exact string match
  for coref in np_list:
    if coref['text'] == guess and coref['id'] != anaphor['id']:
      return coref

  # similar string match
  for coref in np_list:
    if editDifference(None, coref['text'], guess).ratio() > 0.65 and \
       coref['id'] != anaphor['id']:
      return coref

  return None



# nltk tree traversal: http://www.nltk.org/howto/tree.html
# used https://github.com/cmward/hobbs as a reference
# slight tweak of hobbs algorithm
# The sentences must use Treebank tags and be parsed such that they can be
# converted into NLTK Trees. The pronoun must be in the last sentence of the
# file.
#
# This program uses Hobbs' algorithm to find the antecedent of a pronoun. It
# has also been expanded to handle reflexive pronouns. The algorithm is given
# below:
#
# parameters:
# sentence_trees: list of sentence trees. last tree should be the one with the
#                 pronoun
# node_position:  tuple of tree indices to the pronoun node to be resolved
# np_list:        list of anaphors that are the possible nps for the pronoun to
#                 be resolved to
# return:
# None:  if nothing was found
# coref: the np from the np_list that was selected as the np the pronoun
#        resolved to
def hobbs(sentence_trees, node_position, anaphor, np_list):
  # TODO: delete and finish hobbs
  return dirty(sentence_trees, node_position, anaphor, np_list)

  ## 1. Begin at the NP node immediately dominating the pronoun
  #pronoun_sentence_tree = sentence_trees[-1] # pronoun expected to be in last tree
  #dominant_np_position = node_position[:-1]  # strip away last index for parent
  #dom_np_tree = pronoun_sentence_tree[dominant_np_position]

  ## 2. Go up the tree to the first NP or S node encountered. Call this node X
  ##    and the path used to reach it p.
  #search_position = dominant_np_position
  #path = [search_position]
  #while True:
  #  search_position = search_position[:-1] # strip away last index for parent
  #  path.append(search_position)
  #  if pronoun_sentence_tree[search_position].label() == "S" or \
  #     "NP" in pronoun_sentence_tree[search_position].label():
  #    break
  #x = pronoun_sentence_tree[search_position]

  ## 3. Traverse all branches below node X to the left of path p in a
  ##    left-to-right, breadth-first fashion. Propose as an antecedent any NP
  ##    node that is encountered which has an NP or S node between it and X.
  ##for branch in x.subtrees():
  ##  print branch
  ## 4. If node X is the highest S node in the sentence, traverse the surface
  ##    parse trees of previous sentences in the text in order of recency, the
  ##    most recent first; each tree is traversed in a left-to-right,
  ##    breadth-first manner, and when an NP node is encountered, it is proposed
  ##    as an antecedent. If X is not the highest S node in the sentence,
  ##    continue to step 5.
  ## 5. From node X, go up the tree to the first NP or S node encountered. Call
  ##    this new node X, and call the path traversed to reach it p.
  ## 6. If X is an NP node and if the path p to X did not pass through the
  ##    Nominal node that X immediately dominates, propose X as the antecedent.
  ## 7. Traverse all branches below node X to the left of path p in a
  ##    left-to-right, breadth-first manner. Propose any NP node encountered as
  ##    the antecedent.
  ## 8. If X is an S node, traverse all the branches of node X to the right of
  ##    path p in a left-to-right, breadth-first manner, but do not go below any
  ##    NP or S node encountered. Propose any NP node encountered as the
  ##    antecedent.
  ## 9. Go to step 4.
  #return None


def hobbs_reflexive(sentence_trees, node_position, anaphor, np_list):
  return hobbs(sentence_trees, node_position, anaphor, np_list)


def get_tree_position(tree, node):
  for position in tree.treepositions():
    if tree[position] == node:
      return position # tuple of indices
  return ()
