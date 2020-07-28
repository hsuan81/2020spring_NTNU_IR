import os 
import math
import numpy as np
import sys 
sys.path.append('../HW1/')
import function 

"""import codecs
f = codecs.open(u'QUERY_WDID_NEW/20001.query','r','utf-8')
print(f.read())
f.close()"""

def split_termfile(_file) -> list:
    """split the file and store different terms in a list and return the list. """
    answer = []
    for i in _file:
        term = i.split(" ")
        #print("term: {name}".format(name=term))
        term.remove("-1\n")
        answer.extend(term)
    return answer

def split_searchfile(_file) -> list:
    """split the file and store different terms in a list and return the list. """
    answer = []
    dump = []
    for i in _file:
        #print(i)
        term = i.split("\n")
        #print("trimfile: {name}".format(name=term))
        if len(dump) == 3:
            text = term[0].split(" ")
            text.remove("-1")
            #print(text)
            answer.extend(text)
        else:
            dump.append(term)
    return answer

class QueryCorpus:
    def __init__(self, query: list):
        self.query = query
        
        """Count the number of each term in query, build up a term corpus for the query file and return the dictionary"""
        query_corpus = {}
        for i in self.query:
            if i not in query_corpus.keys():
                query_corpus[i] = 1
            else:
                query_corpus[i] += 1
        self.corpus = query_corpus
        self.term_indoc = [0] * len(list(self.corpus.keys()))
        self.word_number = len(query)
        #print(query_corpus)
        #return query_corpus
    def item_number(self):
        return len(list(self.corpus.keys()))

    def number_doc(self, document: list):
        """Calculate the number of document containing the word in the query and return a list."""
        #doc = [0] * self.item_number()
        for i in range(len(document)):
            if document[i] > 0:
                self.term_indoc[i] += 1
                #print(i, document[i])
        # return doc
    
    def length(self, weight_list):
        sum = 0
        for i in weight_list:
            sum += i ** 2
        return math.sqrt(sum)

    def idf(self, number_of_doc: int):
        q_idf = []
        for j in self.term_indoc:
            idf = math.log((number_of_doc)/(0.03+j), 2)  #avoid divided by zero
            q_idf.append(idf)
        return q_idf
    
    def weight(self, idf_list) -> list: 
        q_tf = []
        q_idf = idf_list  #
        q_weight = []
        for i in self.corpus.values():
            f = i / self.word_number
            #f = math.log(i, 2)
            #f = 1 + math.log(i, 2)
            q_tf.append(f)
        
        # for k in range(self.item_number()):
        #     # w = q_tf[k]
        #     w = q_tf[k] * q_idf[k]
        #     q_weight.append(w)
        for k in range(self.item_number()): 
            w = q_tf[k] * q_idf[k]
            q_weight.append(w)
        return q_weight

class DocVector:
    def __init__(self, _file: list, query: list):
        self.word_number = len(_file)
        self.frequency = [0] * len(query)
        for i in range(len(query)):
            if query[i] in _file:
                num = _file.count(query[i])
                self.frequency[i] = num
            # else:
            #     self.frequency.append(0)
        
    def weight(self, idf: list) -> list: 
        d_idf = idf
        d_tf = []
        d_weight = []
        # compute tf of terms in the doc
        for i in self.frequency:
            if i == 0:
                f = 0
            else:
                f = i / self.word_number
                #f = math.log(i, 2)
                #f = 1 + math.log(i, 2)
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

def similarity(query_weight, query_length, doc_weight, doc_weight_length):
    # product = 0
    # for i in range(len(query_weight)):
    #     p = query_weight[i] * doc_weight[i]
    #     product += p
    product = np.dot(query_weight, doc_weight)
    if doc_weight_length == 0:
        rank = 0
    else:
        rank = product / (doc_weight_length * query_length)
    return rank

def vector_space_model(query_content, doc_order, all_doc):
    que1 = QueryCorpus(query_content)
    all_doc_vector = []
    for passage in all_doc:
        doc1 = DocVector(passage, list(que1.corpus.keys()))
        term_num_doc = que1.number_doc(doc1.frequency)
        all_doc_vector.append(doc1)
    
    #print(que1.term_indoc)
    #print(que1.corpus.values())
    que1_idf = que1.idf(2265)
    #print("idf", que1_idf)
    que1_weight = que1.weight(que1_idf)
    que1_length = que1.length(que1_weight)
    #print("weight", que1_weight)
    all_doc_weight = []
    all_doc_rank = []
    for i in range(len(all_doc_vector)):
        w = all_doc_vector[i].weight(que1_idf)
        all_doc_weight.append(w)
        rank = similarity(que1_weight, que1_length, w, all_doc_vector[i].length(w))
        all_doc_rank.append([doc_order[i], rank])
    all_doc_rank.sort(key= lambda x: x[1], reverse=True)
    #print("total rank", all_doc_rank)
    #all_query_result = []
    q1_result = []
    for i in all_doc_rank:
        q1_result.append(i[0])
    #print(q1_result)
    #all_query_result.append(q1_result)
    return all_doc_rank, q1_result

all_doc = []
doc_order = []
for root, dirs, files in os.walk("./SPLIT_DOC_WDID_NEW", topdown=False):
    for name in files:
        if name[0] == "V":
            doc_order.append(name)
            with open(os.path.join(root, name), "r") as doc:
                f = split_searchfile(doc)
                all_doc.append(f)



all_query = []
query_order = []
for root, dirs, files in os.walk("./QUERY_WDID_NEW", topdown=False):
    for name in files:
        if name[0] == "2":
            query_order.append(name)
            with open(os.path.join(root, name), "r") as q:
                f = split_termfile(q)
                all_query.append(f)

q1 = QueryCorpus(all_query[0])
doc1 = DocVector(all_doc[0], list(q1.corpus.keys()))
if "VOM19980220.0700.1159" in doc_order:
    index = doc_order.index('VOM19980220.0700.1159')
doc2 = DocVector(all_doc[index], list(q1.corpus.keys()))
# print(doc_order[0])
# print(doc_order[index])

# print(len(q1.query), len(q1.corpus.keys()))
# print(len(doc1.frequency), len(q1.term_indoc))
# print(len(doc2.frequency))
#print("before", q1.term_indoc)
#print("d1 raw count", doc1.frequency)
#print("d2 raw count", doc2.frequency)
for i in range(len(all_doc)):
    d = DocVector(all_doc[i], list(q1.corpus.keys()))
    q1.number_doc(d.frequency)
# q1.number_doc(doc1.frequency)
# q1.number_doc(doc2.frequency)
idf = q1.idf(2265)
#print("after",q1.term_indoc)
#print("idf", idf)
d1_weight = doc1.weight(idf)
d2_weight = doc2.weight(idf)
# print("d1",d1_weight)
# print("d2",d2_weight)
q1_weight = q1.weight(idf)
q1_length = q1.length(q1_weight)
#print("q1_weight", q1_weight)
d1_rank = similarity(q1_weight, q1_length, d1_weight, doc1.length(d1_weight))
d2_rank = similarity(q1_weight, q1_length, d2_weight, doc2.length(d2_weight))
# # print("d1 rank",d1_rank)
# # print("d2 rank",d2_rank)

allrank, result = vector_space_model(all_query[0], doc_order, all_doc)
with open("test_result.txt", "w") as test:
    for i in range(len(allrank)):
        test.write(allrank[i][0]+"  rank:  " + str(allrank[i][1])+"\n")
with open("query_weight.txt", "w") as a:
    for i in range(len(q1_weight)):
        a.write("count: " + str(list(q1.corpus.values())[i]))
        a.write("  doc_num: " + str(q1.term_indoc[i]))
        a.write("  idf: " + str(idf[i]))
        a.write("  weight: " + str(q1_weight[i]) + "\n")

all_result = []
for i in range(len(all_query)):
    doc_rank, result = vector_space_model(all_query[i], doc_order, all_doc)
    all_result.append(result)


#Compute mean average precision for the search system
with open('HW1_AssessmentTrainSet.txt', 'r') as relevant_set:
    relevance = function.split_file(relevant_set)

total_ap = 0
for i in range(16):
    mAP = function.mean_average_precision(all_result[i], relevance[i])
    total_ap += mAP
total_map = round(total_ap/16, 8)
map_answer = "mAP = " + str(total_map)
print(map_answer)

#print(all_doc_rank)
#print(all_doc_rank)

# print(all_doc_vector[0].frequency)
# print(all_doc_weight[0])



        
