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

class QueryCorpus:
    def __init__(self, query: list):
        """Count the number of each term in query, build up a term corpus for the query file and return the dictionary"""
        self.query = query
        query_corpus = {}
        for i in self.query:
            if i not in query_corpus.keys():
                query_corpus[i] = 1
            else:
                query_corpus[i] += 1
        self.corpus = query_corpus
        self.term_indoc = [0] * len(list(self.corpus.keys()))
        
    def item_number(self):
        return len(list(self.corpus.keys()))

    def number_doc(self, document: list):
        """Calculate the number of document containing the word in the query and return a list."""
       
        for i in range(len(document)):
            if document[i] > 0:
                self.term_indoc[i] += 1
        
    
    def length(self, weight_list):
        sum = 0
        for i in weight_list:
            sum += i ** 2
        return math.sqrt(sum)

    def idf(self, number_of_doc: int):
        q_idf = []
        for j in self.term_indoc:
            if j == 0:
                idf = 0
            else:
                idf = math.log((number_of_doc+1)/(j), 10)  #avoid divided by zero
            q_idf.append(idf)
        return q_idf

    def bm_idf(self, number_of_doc: int):
        q_idf = []
        for i in self.term_indoc:
            idf = math.log((number_of_doc - i + 0.5)/(i + 0.5), 2)
            q_idf.append(idf)
        return q_idf
        

    def weight(self, idf_list) -> list: 
        q_tf = []
        q_idf = idf_list  #
        q_weight = []
        for i in self.corpus.values():
            f = math.log(i, 10) + 4
            q_tf.append(f)
        
        for k in range(self.item_number()): 
            w = q_tf[k] * q_idf[k]
            q_weight.append(w)
        return q_weight

class DocVector:
    def __init__(self, one_file: list, query: list):
        self.frequency = [0] * len(query)
        for i in range(len(query)):
            if query[i] in one_file:
                num = one_file.count(query[i])
                self.frequency[i] = num
        self.word_length = len(one_file)
        
        
    def weight(self, idf: list) -> list: 
        d_idf = idf
        d_tf = []
        d_weight = []
        # compute tf of terms in the doc
        for i in self.frequency:
            if i == 0:
                f = 0
            else:
                f = math.log(i, 10) + 4
            d_tf.append(f)

        for k in range(len(d_idf)):
            w = d_tf[k] * d_idf[k]
            d_weight.append(w)
        return d_weight
        
    def length(self, weight_list):
        sum = 0
        for i in weight_list:
            sum += i ** 2
        return math.sqrt(sum)
    
    def bm_score(self, idf, avg_length, k1, b):
        sum = 0
        for i in range(len(self.frequency)):
            score = idf[i]*(self.frequency[i]*(k1 + 1)/(self.frequency[i]+k1*(1-b+b*self.word_length/avg_length)))
            sum += score
        return sum

def similarity(query_weight, query_length, doc_weight, doc_weight_length):

    product = np.dot(query_weight, doc_weight)
    if doc_weight_length == 0:
        rank = 0
    else:
        rank = product / (doc_weight_length * query_length)
    return rank

def vector_space_model(query_content: list, doc_order, all_doc):
    que1 = QueryCorpus(query_content)
    all_doc_vector = []
    for passage in all_doc:
        doc1 = DocVector(passage, list(que1.corpus.keys()))
        term_num_doc = que1.number_doc(doc1.frequency)
        all_doc_vector.append(doc1)
    
    que1_idf = que1.idf(2265)
    que1_weight = que1.weight(que1_idf)
    que1_length = que1.length(que1_weight)
    all_doc_weight = []
    all_doc_rank = []
    for i in range(len(all_doc_vector)):
        w = all_doc_vector[i].weight(que1_idf)
        all_doc_weight.append(w)
        rank = similarity(que1_weight, que1_length, w, all_doc_vector[i].length(w))
        all_doc_rank.append([doc_order[i], rank])
    all_doc_rank.sort(key= lambda x: x[1], reverse=True)
    q1_result = []
    for i in all_doc_rank:
        q1_result.append(i[0])
    return all_doc_rank, q1_result

def BM_25(query_content, doc_order, all_doc):
    k1 = 2.0
    b = 0.75
    que1 = QueryCorpus(query_content)
    all_doc_vector = []
    avg_length = 0
    for passage in all_doc:
        doc1 = DocVector(passage, list(que1.corpus.keys()))
        term_num_doc = que1.number_doc(doc1.frequency)
        all_doc_vector.append(doc1)
        avg_length += doc1.word_length
    avg_length = avg_length / len(all_doc_vector)

    que1_idf = que1.bm_idf(2265)
    
    all_doc_rank = []
    for i in range(len(all_doc_vector)):
        score = all_doc_vector[i].bm_score(que1_idf, avg_length, k1, b)
        all_doc_rank.append([doc_order[i], score])
    all_doc_rank.sort(key= lambda x: x[1], reverse=True)

    q1_result = []
    for i in all_doc_rank:
        q1_result.append(i[0])
    return all_doc_rank, q1_result


def word_collection(doc_text_lis):
    collection = [] 
    for one_doc in doc_text_lis:
        for term in one_doc:
            if term not in collection:
                collection.append(term)
    return collection

# def relevant_vector(relevant_docs_lis, docs_frequency_vector):
#     relevant_freq = {}
#     for doc, freq in docs_frequency_vector.items():
#         if doc in relevant_docs_lis:
#             relevant_freq[doc] = docs_frequency_vector[doc]
#     return relevant_freq

def relevant_text(docs_order, all_docs, relevant_docs_lis):
    relevant_text = []
    for relevants in relevant_docs_lis:
        docs = []
        for doc in relevants:
            index = docs_order.index(doc)
            docs.append(all_docs[index])

        relevant_text.append(docs)
    return relevant_text


class WordVector:
    def __init__(self, docList, docText: list, word_collection):
        self.docList = docList
        self.docText = docText
        self.wordList = word_collection 
        # for one_doc in docText:
        #     for term in one_doc:
        #         if term not in self.wordList:
        #             self.wordList.append(term)
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
        #freqList = [0] * len(self.wordList)
        for doc, freq in frequency.items():
            #freqList = [0] * len(self.wordList)
            freq_dict = {}
            for term, num in freq.items():
                tf = 1 + math.log(num, 10)
                total = num * idf_dict[term]
                freq_dict[term] = total
                #freqList[self.wordIndex[term]] = 1 + math.log(f, 10)
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
            #q_tf_idf[self.wordIndex[q]] = 1 + math.log(f, 10)
            q_tf_idf[q] = f
        return q_tf_idf

    def length(self, query_tf_idf: dict):
        sum = 0
        for weight in query_tf_idf.values():
            sum += weight ** 2
        length = math.sqrt(sum)   
        return length

def docs_similarity(one_query_vector: dict, query_length, docs_vector: dict, docs_length: dict):
    #q_np = np.array(one_query_vector)
    docs_rank = []
    for doc, vector in docs_vector.items():
        sum = 0
        for q in one_query_vector.keys():
            if q in vector.keys():
                sum += one_query_vector[q] * vector[q]
        score = sum / (query_length * docs_length[doc])
        docs_rank.append([doc, score])
        

    # for doc, vector in docs_vector.items():
    #     # doc_np = np.array(docs_vector[doc])
    #     # product = np.dot(q_np, doc_np)
    #     if docs_length[doc] == 0:
    #         rank = 0
    #     else:
    #         rank = product / (query_length * docs_length[doc])
    #     docs_rank.append([doc, rank])
    return docs_rank


def vsm(one_query: list, docs_list, docs_text, word_collection):
    docs = WordVector(docs_list, docs_text, word_collection)
    que = QueryVector(docs.wordList, one_query)
    q_idf = que.idf(docs.docs_frequency())
    #q_freq = que.query_frequency()
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
    

    #
    # all_doc_vector = []
    # for passage in all_doc:
    #     doc1 = DocVector(passage, list(que1.corpus.keys()))
    #     term_num_doc = que1.number_doc(doc1.frequency)
    #     all_doc_vector.append(doc1)
    
    # que1_idf = que1.idf(2265)
    # que1_weight = que1.weight(que1_idf)
    # que1_length = que1.length(que1_weight)
    # all_doc_weight = []
    # all_doc_rank = []
    # for i in range(len(all_doc_vector)):
    #     w = all_doc_vector[i].weight(que1_idf)
    #     all_doc_weight.append(w)
    #     rank = similarity(que1_weight, que1_length, w, all_doc_vector[i].length(w))
    #     all_doc_rank.append([doc_order[i], rank])
    # all_doc_rank.sort(key= lambda x: x[1], reverse=True)
    # q1_result = []
    # for i in all_doc_rank:
    #     q1_result.append(i[0])
    # return all_doc_rank, q1_result






    









        
