import os 
import math
import numpy as np
from docx import Document
from docx.shared import Cm
from docx.shared import Pt
import function 

def split_short_termfile(_file) -> list:
    """split the file and store different terms in a list and return the list. """
    answer = []
    for i in _file:
        term = i.split(" ")
        term.remove("-1")
        term.remove("\n")
        answer.extend(term)
    return answer

def split_termfile(_file) -> list:
    """split the file and store different terms in a list and return the list. """
    answer = []
    for i in _file:
        term = i.split(" ")
        term.remove("-1\n")
        answer.extend(term)
    return answer

def split_searchfile(_file) -> list:
    """split the file and store different terms in a list and return the list. """
    answer = []
    dump = []
    for i in _file:
        term = i.split("\n")
        if len(dump) == 3:
            text = term[0].split(" ")
            text.remove("-1")
            answer.extend(text)
        else:
            dump.append(term)
    return answer

def word_collection(doc_text_lis):
    collection = [] 
    for one_doc in doc_text_lis:
        for term in one_doc:
            if term not in collection:
                collection.append(term)
    return collection


def relevant_text(docs_order, all_docs, one_q_relevant_docs_lis):
    relevant_text = []
    for relevants in one_q_relevant_docs_lis:
        index = docs_order.index(relevants)
        relevant_text.append(all_docs[index])
    return relevant_text


class WordVector:
    def __init__(self, docList, docText: list, word_collection):
        self.docList = docList
        self.docText = docText
        self.wordList = word_collection 
        self.wordIndex = {}
        for word in self.wordList:
            self.wordIndex[word] = self.wordList.index(word)

    def docs_frequency(self)-> dict:
        """compute the occurence of words from collection for each doc, 
        and return a dictionary with doc as key and term and its frequency in the form of dictionary for value.""" 
        docsTermFreq = {}
        # Compute word frequency of each doc
        for doc in self.docList:
            d_id = self.docList.index(doc)
            text = self.docText[d_id]
            frequency = {}
            for term in text:
                if term in frequency.keys():
                    frequency[term] += 1
                else:
                    frequency[term] = 1
            docsTermFreq[doc] = frequency
        return docsTermFreq
    
    def docs_tf_idf(self, idf_dict)-> dict:
        """compute the tf-idf of words from term frequency for each doc and corresponding idf in dictionary, 
        and return a dictionary with doc as key and term and its tf-idf in the form of dictionary for value.""" 
        docs_term_tf = {}
        frequency = self.docs_frequency()
        for doc, freq in frequency.items():
            freq_dict = {}
            for term, num in freq.items():
                tf = 1 + math.log(num, 10)
                total = num * idf_dict[term]
                freq_dict[term] = total
            docs_term_tf[doc] = freq_dict
        return docs_term_tf

    def length(self, docs_tf_idf)-> dict:
        """Compute the length of each doc vector and return a dictionary with doc as key and length as value"""
        docs_length = {}
        for doc, weight in docs_tf_idf.items():
            sum = 0
            for w in weight.values():
                sum += w ** 2
            length = math.sqrt(sum)
            docs_length[doc] = length   
        return docs_length

class QueryVector:
    def __init__(self, wordList, oneQueryText: list):
        self.query = oneQueryText
        self.wordlist = wordList
        # self.wordIndex = wordIndex
        self.docs_num = 2265

    def idf(self, docs_frequency):
        term_num_in_docs = {}
        for doc, terms in docs_frequency.items():
            for word, freq in terms.items():
                if word in term_num_in_docs:
                    term_num_in_docs[word] += 1
                else:
                    term_num_in_docs[word] = 1
        term_idf = term_num_in_docs
        for term, freq in term_idf.items():
            term_idf[term] = math.log(self.docs_num/freq, 10)
        return term_idf

    def query_frequency(self)-> dict:
        TermFreq = {}
        #term_order = {}
        for q in self.query:
            if q in self.wordlist:
                if q in TermFreq.keys():
                    TermFreq[q] += 1
                else:
                    TermFreq[q] = 1
        return TermFreq
    
    def query_tf_idf(self, idf) -> dict:
        #q_tf_idf = [0] * len(self.wordlist)
        q_tf_idf = {}
        frequency = self.query_frequency()
        for q, freq in frequency.items():
            f = (1 + math.log(freq, 10)) * idf[q]
            q_tf_idf[q] = f
        return q_tf_idf

    def length(self, query_tf_idf: dict):
        sum = 0
        for weight in query_tf_idf.values():
            sum += weight ** 2
        length = math.sqrt(sum)   
        return length

def docs_similarity(one_query_vector: dict, query_length, docs_vector: dict, docs_length: dict):
    docs_rank = []
    for doc, vector in docs_vector.items():
        sum = 0
        for q in one_query_vector.keys():
            if q in vector.keys():
                sum += one_query_vector[q] * vector[q]
        score = sum / (query_length * docs_length[doc])
        docs_rank.append([doc, score])
    return docs_rank


def vsm(one_query: list, docs_list, docs_text, word_collection):
    docs = WordVector(docs_list, docs_text, word_collection)
    que = QueryVector(docs.wordList, one_query)
    q_idf = que.idf(docs.docs_frequency())
    q_tf_idf = que.query_tf_idf(q_idf)
    q_len = que.length(q_tf_idf)
    docs_tf_idf = docs.docs_tf_idf(q_idf)
    docs_len = docs.length(docs_tf_idf)

    ranks = docs_similarity(q_tf_idf, q_len, docs_tf_idf, docs_len)
    ranks.sort(key=lambda x: x[1], reverse=True)
    docs_order = []
    for i in range(len(ranks)):
        docs_order.append(ranks[i][0])
    return docs_order, ranks
    







    









        
