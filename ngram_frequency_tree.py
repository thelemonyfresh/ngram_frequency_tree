import nltk
from nltk.probability import FreqDist
from nltk.util import ngrams
from numpy import *

def ngram_tree(input_text, n_max=10, stopwords=[]):
    """Create an ngram frequency tree from a string of text.

    Args:
        input_text (string): text used to build ngram frequency tree
        n_max (int): the maximum depth of the tree, or the maximum ngram length to be included in the tree
        stopwords (list of strings): list of words to be excluded from ngram frequency counting (exclude standard english using nltk.corpus.stopwords.words('english')
        
    Returns:
        List of Ngram "root" objects with no parents (typically 1-grams) which are cannot be reduced to an (n-1)gram that occurs in the text. List is ordered by occurrence frequency of root in input string.
     """

    freqdist = ngram_filter(ngram_freq(input_text,n_max),stopwords)

    ngram_root_list = []
    for n in arange(1,n_max+1):
        for gramtuple in sel_freq_n(freqdist,n).most_common():
            gram = Ngram(gramtuple[0],gramtuple[1])
            is_added=False
            for subgram in ngram_root_list:
                if contains_subgram(gram,subgram):
                    is_added=True
                    subgram.add_child(gram)
            if not is_added:
                ngram_root_list.append(gram)

    return sorted(ngram_root_list,key=lambda ngram_object: ngram_object.frequency, reverse=True)

class Ngram():
    """ Class containing nodes of ngram tree.

    Args:
        ngram_tuple: tuple representation of ngram
        frequency: occurrence frequency associated with ngram
        is_in: list of children Ngrams

    Methods:
        add_child(ngram_object): add Ngram object to list of children, recursively if Ngram object belongs as a subchild to one of this Ngram's list of children
        get_children(): return list of children Ngram objects

    """
    def __init__(self,tokens,freq):
        self.ngram_tuple = tokens # tuple of this ngram
        self.frequency = freq # frequency of this ngram
        self.is_in = [] # list of children

    def __str__(self):
        output_str = self.ngram_tuple[0]
        for word in self.ngram_tuple[1:]:
            output_str += " " + word
        return output_str

    def add_child(self,ngram_object):
        is_added=False
        for gram in self.is_in:
            if contains_subgram(ngram_object,gram) and not is_added: # check if existing children contain ngram_object
                is_added=True
                gram.add_child(ngram_object) # recurse to add to the deepest child node in the branch
            elif ngram_object.ngram_tuple == gram.ngram_tuple and not is_added: # do not added duplicates
                is_added=True
        if not is_added:
            self.is_in.append(ngram_object)
            self.is_in = sorted(self.is_in,key=lambda ngram_object: ngram_object.frequency, reverse=True)

    def add_child_list(self,child_list):
        self.is_in = child_list

    def get_children(self):
        return self.is_in

### NGRAM COUNTING AND DISTRIBUTION CREATION

def ngram_freq(textstring, max_n=10):
    """ Construct an ngram frequency distribution from a string for 0 < n < max_n.

    Args:
        textstring: string to extract ngrams from
        max_n: the longest ngram length counted

    Returns:
        FreqDist obeject with tuple representation of ngrams as keys and the frequency with which each ngram occurs in textstring
    """

    tokenlist = nltk.Text(nltk.word_tokenize(textstring))
    
    ngram_freqdist = FreqDist()
    for n in arange(1,max_n):
        for gram in ngrams(tokenlist,n):
            ngram_freqdist[gram] += 1
  
    return ngram_freqdist

def ngram_filter(input_freqdist,stopwords=[]):
    """ Filter frequency distribution of ngrams.
    
    Removes:
    1. ngrams consisting of only stopwords (given in "stopwords" list; exclude standard english using nltk.corpus.stopwords.words('english')
    2. ngrams that occur only in higher ngrams (if freq('the')==freq('and the'), e.g.)
    3. ngrams with freq=1

    Args:
        ngram_freqdist: frequency distribution of ngrams
        additional_stopwords: stopwords to be removed.

    Returns:
        Filtered FreqDist with tuple representations of ngrams as keys.

    """
    ngram_freqdist = input_freqdist.copy()
    
    # remove ngrams of only stop words
    for tuple in ngram_freqdist.most_common():
        isin = []
        for word in tuple[0]: 
            isin.append(word in stopwords)
        if all(isin): ngram_freqdist.pop(tuple[0])

    # remove ngrams which are only duplicate parts of higher ngrams
    for tuple in ngram_freqdist.most_common():
        for j in arange(1,len(tuple[0])):
            for gram in ngrams(tuple[0],j):
                if ngram_freqdist[gram] == ngram_freqdist[tuple[0]] > 0:
                    ngram_freqdist.pop(gram)
                    
    # remove ngrams occurring only once in a text
        if ngram_freqdist.has_key(tuple[0]) and tuple[1]<2: ngram_freqdist.pop(tuple[0])

    return ngram_freqdist

### NRGAM, FREQDIST OPERATORS

def sel_freq_n(freqdist,n=1):
    """ Return frequency distribution with only ngrams of length n.

    Args:
        freqdist: a frequency distribution of ngram tuples
        n: desired length of ngram tuples
        
    Returns:
        FreqDist object with tuple representation of ngrams as keys.
    """
    freq_n = FreqDist()
    for gram in freqdist.most_common():
        if len(gram[0]) == n:
            freq_n[gram[0]] += freqdist[gram[0]]
    return freq_n

def contains_subgram(ngram,mgram):
    """ Determine if mgram is contained within ngram (Ngram objects).

    Example (using tuple representation):
        "the brown dog" contains "brown dog"

        If "ngram" is an Ngram object for the phrase "the brown dog" and "mgram" is an Ngram object for the phrase "brown dog":
        contains_subgram(ngram,mgram) -> True
        contains_subgram(mgram,ngram) -> False

    Args:
        ngram: ngram possibly containing mgram
        mgram: possibly contained within ngram
    """
    is_in = False
    if len(ngram.ngram_tuple) > len(mgram.ngram_tuple):
        for i in arange(0,len(ngram.ngram_tuple)-len(mgram.ngram_tuple)+1):
             if ngram.ngram_tuple[i:i+len(mgram.ngram_tuple)] == mgram.ngram_tuple:
                is_in = True

    return is_in

### OUTPUT

def ngram_tree_to_emacs(root,level='* '):
    """ Produce a string for output to Emacs Outline mode of an ngram tree (single root). 
    
    Produce string Outline-hierarchy representation of this node and all its children. Of the form: "* rootnode1 /n ** childnode1 /n **childnode2 /n etc..."

    Args:
        root: root Ngram node to be represented.
        level: emacs Outline-mode starting level
        
    Returns:
        String with Outline-mode representation of Ngram object and its children.
    """

    text_string =  level + "[" + str(root.frequency) + "]" + str(root) + '\n'
    if root.get_children != []:
        for ngram in root.get_children():
            text_string += ngram_tree_to_emacs(ngram,"*" + level)
    return text_string


def ngram_tree_to_html(root):
    """ Produce a string for output to an html ul of an ngram tree (single root).
    
    Args:
        root: root Ngram node
        
    Returns:
        String with html ul representation of Ngram object and its children.
    """
    text_string =  '' 
    if len(root.get_children())>0:
        text_string += '<li title="' + str(root) + '">' + "[" + str(root.frequency) + "] " + str(root) + ' + <ul>'
        for ngram in root.get_children():
            text_string += ngram_tree_to_html(ngram)
        text_string += "</ul></li>" 
    if len(root.get_children()) == 0: 
        text_string += '<li title="' + str(root) + '">' + "[" + str(root.frequency) + "] " + str(root) + ' </li>'

    return text_string
    
