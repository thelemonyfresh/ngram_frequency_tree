# ngram_frequency_tree


An Ngram Frequency Tree is an ordered representation of ngram occurrence frequency in a text, where ngrams are children of (n-1)grams in which they occur in that text. This module requires NLTK.


Take the example sentence: "The quick brown fox jumps over the lazy dog and the lazy cat." There are many possible ngrams in this sentence, but an exhaustive list is not very useful. Consider only those that occur more than once, namely:


- the (freq=3)
- the lazy (freq=2)


Which can be arranged simply into a frequency tree with one parent node ("the", freq=2) with one child ("the lazy", freq=3).

Ngram Frequency Trees are frequency-sorted lists of root ngram nodes (often a list of 1-grams), each associated with a frequency-sorted list of higher-order children each itself a node.

## How to use

The main method is `ngram_tree(string)` which, without additional arguments, counts all ngrams with n<10 and builds a tree as described above. It returns a frequency sorted list of root `Ngram` objects. It also accepts optional arguments `ngram_tree(string, n_max, stopwords_list)` where n_max is the longest ngram it will consider and stopwords_list is a list of words to be excluded from counting.

`Ngram` objects have the following properties:

- `str(Ngram)` returns a string representation of the ngram
- `Ngram.frequency` stores the occrrence frequency of the ngram
- `Ngram.get_children()` returns a frequency-sorted list of children, also `Ngram` objects


The NLTK tokenizer used automatically keeps all punctuation, so punctuation is counted as part of the ngrams. To remove common English words and punctuation, use the `stopwords` argument:
```
ngram_tree(text_string, stopwords=nltk.corpus.stopwords.words('english')+['.',',','!','?','(',')',':',';'])
```


### Output

`ngram_tree_to_emacs(Ngram)` takes a single Ngram node and recursively returns a string representation of this node and all its children in [Emacs Outline Mode](https://www.emacswiki.org/emacs/OutlineMode) hierarchical format.


`ngram_tree_to_html(Ngram)` takes a single Ngram node and recursively returns a string representation of this node and all its children in the form of nested HTML "ul" hierarchical format.


To output an entire tree, you need to loop over all root nodes in the tree list:

```
output_string = ''
for node in ngram_tree:
  output_string += ngram_tree_to_html(node)
```
