import os
from utility_func import *
from inverted_index import *

query_set = []
with open("listtdt2qry_OutSideforTrain.txt", "r") as c:
    for q in c:
        query_set.append(q[:-1])
# print(len(query_set))
# print(query_set[:5])

# establish corpus dictionary
with open("Word_Unigram_Xinhua98Upper.txt", "r") as c:
    corpus = split_corpus(c)

all_doc = []
doc_order = []
for root, dirs, files in os.walk("./SPLIT_DOC_WDID_NEW/", topdown=False):
    for name in files:
        if name[0] == "V":
            doc_order.append(name)
            with open(os.path.join(root, name), "r") as doc:
                f = split_searchfile(doc)
                all_doc.append(f)



all_query = []
query_order = []
for root, dirs, files in os.walk("./TDT2-TrainingQueries", topdown=False):
    for name in files:
        if name[0] == "X" and name in query_set:
            query_order.append(name)
            with open(os.path.join(root, name), "r") as q:
                f = split_termfile(q)
                all_query.append(f)
                # print(name)
# print(len(query_order))
# print(len(all_query))

with open('QDRelevanceTDT2_forHMMOutSideTrain.txt', 'r') as relevant_set:
    relevance, relevance_name = split_training_file(relevant_set, query_order)
print(len(relevance_name))
# print(all_query[0])
# print(query_order[:5])

# establish document database
doc_db = Database()
for doc in doc_order:
    ind = doc_order.index(doc)
    doc_db.add_index(doc, ind)
    doc_db.add_length(ind, len(all_doc[ind]))

# establish document inverted index
inverted_file = InvertedIndex(doc_db)
for text in all_doc:
    inverted_file.index_document(all_doc.index(text), text)

# caulculate the query likelihood of documents
docs_freq = dict()
docs_length = dict()
for doc in doc_order:
    doc_id = doc_db.get_index(doc)
    doc_length = doc_db.get_length(doc)
    wordfreq_dict = inverted_file.lookup_terms_freq(all_doc[doc_id], doc_id)
    docs_freq[doc] = wordfreq_dict
    docs_length[doc] = doc_length

result = []
doc_result = []
for query in all_query:
    q_rank = query_likelihood(docs_freq, docs_length, corpus, query)
    q_order = [s[0] for s in q_rank]
    result.append(q_rank)
    doc_result.append(q_order)


# mAP for query likelihood 
# with open('QDRelevanceTDT2_forHMMOutSideTrain.txt', 'r') as relevant_set:
#     relevance, relevance_name = split_training_file(relevant_set)
#     # relevance = split_file(relevant_set, len(query_order))

# compute the mAP
total_ap = 0
rele_num = 0
for i in range(len(query_order)):
    if query_order[i] in relevance_name:
        rele_num += 1
        ind = relevance_name.index(query_order[i])
        mAP = mean_average_precision(doc_result[i], relevance[ind])
        total_ap += mAP
total_map = round(total_ap/rele_num, 8)
print(total_map)