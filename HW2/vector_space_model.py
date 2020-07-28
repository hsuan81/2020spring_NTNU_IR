import os 
import math
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
        self.term_indoc = [0] * len(self.corpus.keys())
        #print(query_corpus)
        #return query_corpus
    def item_number(self):
        return len(self.corpus.keys())

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
            # if j == 0:
            #     idf = 0
            # else:
            idf = math.log(number_of_doc/(1+j), 2)  #avoid divided by zero
            q_idf.append(idf)
        return q_idf
    
    def weight(self, idf_list) -> list: 
        q_tf = []
        q_idf = idf_list  #
        q_weight = []
        for i in self.corpus.values():
            if i == 0:
                f = 0
            else:
                f = 1 + math.log(i, 2)
            q_tf.append(f)
        #print("tf", q_tf)
        # for j in self.doc:
        #     if j == 0:
        #         idf = 0
        #     else:
        #         idf = math.log(total_doc/j, 2)
        #     q_idf.append(idf)
        for k in range(self.item_number()):
            #if q_idf[k] == 0:
             #   q_weight.append(w)
            w = q_tf[k] * q_idf[k]
            q_weight.append(w)
        return q_weight

class DocVector:
    def __init__(self, _file: list, query: list):
        self.frequency = []
        for i in query:
            if i in _file:
                num = _file.count(i)
                self.frequency.append(num)
            else:
                self.frequency.append(0)
        
    def weight(self, idf: list) -> list: 
        d_idf = idf
        d_tf = []
        d_weight = []
        # compute tf of terms in the doc
        for i in self.frequency:
            if i == 0:
                f = 0
            else:
                f = 1 + math.log(i, 2)
            d_tf.append(f)
        # for j in self.doc:
        #     if j == 0:
        #         idf = 0
        #     else:
        #         idf = math.log(total_doc/j, 2)
        #     d_idf.append(idf)
        # compute tf-idf of terms
        for k in range(len(d_idf)):
            w = d_tf[k] * d_idf[k]
            d_weight.append(w)
        return d_weight
        
    def length(self, weight_list):
        sum = 0
        for i in weight_list:
            sum += i ** 2
        return math.sqrt(sum)

def similarity(query_weight, doc_weight, doc_weight_length):
    product = 0
    for i in range(len(query_weight)):
        p = query_weight[i] * doc_weight[i]
        product += p
    if doc_weight_length == 0:
        rank = 0
    else:
        rank = product / doc_weight_length
    return rank


#file_path = path.relpath("QUERY_WDID_NEW/20001.query")
# with open("QUERY_WDID_NEW/20001.query", "r") as q1:
#     query1 = split_termfile(q1)
#print(query1)
# with open("SPLIT_DOC_WDID_NEW/VOM19980220.0700.0166", "r") as f1:
#     file1 = split_searchfile(f1)
#print(file1)

# folderpath = r"SPLIT_DOC_WDID_NEW" # make sure to put the 'r' in front
# filepaths  = [os.path.join(folderpath, name) for name in os.listdir(folderpath)]
# all_doc = []
# for path in filepaths:
#     print(path)
#     with open(path, "r", errors = "ignore") as doc:
#         f = split_searchfile(doc)
#         all_doc.append(f)

def vector_space_model(query_content, doc_order, all_doc):
    que1 = QueryCorpus(query_content)
    all_doc_vector = []
    for passage in all_doc:
        doc1 = DocVector(passage, que1.corpus.keys())
        term_num_doc = que1.number_doc(doc1.frequency)
        all_doc_vector.append(doc1)
    #print(que1.term_indoc)
    #print(que1.corpus.values())
    que1_idf = que1.idf(2265)
    #print("idf", que1_idf)
    que1_weight = que1.weight(que1_idf)
    #print("weight", que1_weight)
    all_doc_weight = []
    all_doc_rank = []
    for i in range(len(all_doc_vector)):
        w = all_doc_vector[i].weight(que1_idf)
        all_doc_weight.append(w)
        rank = similarity(que1_weight, w, all_doc_vector[i].length(w))
        all_doc_rank.append([doc_order[i], rank])
    all_doc_rank.sort(key= lambda x: x[1], reverse=True)
    #all_query_result = []
    q1_result = []
    for i in all_doc_rank:
        q1_result.append(i[0])
    #print(q1_result)
    #all_query_result.append(q1_result)
    return q1_result

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

all_result = []
for i in range(len(all_query)):
    result = vector_space_model(all_query[i], doc_order, all_doc)
    all_result.append(result)

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



#print("query corpus", que1.corpus)
#print(len(que1.corpus.values()))
#doc1 = DocVector(file1, que1.corpus.keys())
#print("doc1", doc1.frequency)
#print(len(doc1.frequency))
# term_num_doc = que1.number_doc(doc1.frequency)
# idf_list = que1.idf(2, term_num_doc)
# print("query1", que1.corpus.values())
# print("doc", doc1.frequency)
# print("idf", idf_list)
# test = que1.weight(2, idf_list)
# print(test)

#qq1 = que1.term_corpus()
#q1_frequency = term_corpus(query1)
#print("count", query1.count("3015"))
#f1_q1 = []
# for i in que1.corpus.keys():
#     if i in file1:
#         num = file1.count(i)
#         f1_q1.append(num)
#         #q1_frequency[i] += 1
#         #print(i,q1_frequency[i])
#     else:
#         f1_q1.append(0)
# print(f1_q1)
#print(q1_frequency.values())
        
