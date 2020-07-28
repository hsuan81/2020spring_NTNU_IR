import os
import numpy as np
from numpy import inf
from search_system import *
from function import *
import time
start_time = time.time()

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

                
query_number = len(all_query)
word_lis = word_collection(all_doc)
# vector space model
all_result1 = []
for i in range(len(all_query)):
    result, ranks = vsm(all_query[i], doc_order, all_doc, word_lis)
    all_result1.append(result)


# mAP for vector space model
with open('HW1_AssessmentTrainSet.txt', 'r') as relevant_set:
    relevance = function.split_file(relevant_set)
# compute the mAP
total_ap1 = 0
for i in range(query_number):
    mAP = function.mean_average_precision(all_result1[i], relevance[i])
    total_ap1 += mAP
total_map1 = round(total_ap1/query_number, 8)
map_answer1 = "mAP = " + str(total_map1)
print("mAP before  ex", map_answer1)

# order the doc content according to the rank
# result_doc_text = []
# for i in range(len(all_result1)):
#     result = []
#     for j in all_result1[i]:
#         #print(all_result1[i])
#         index = doc_order.index(j)
#         text = all_doc[index]
#         result.append(text)
#     result_doc_text.append(result)


# # Rocchio method
# with open('./HW1_AssessmentTrainSet.txt', 'r') as relevant_set:
#     relevance = function.split_file(relevant_set)
# remove_newline_symbol(relevance)

# docs = WordVector(doc_order, all_doc, word_lis)
# docs_freq = docs.docs_frequency()
# optimal_q_vector = []
# optimal_qlis = []
# optimal_q_length = []
# for i in range(16):
#     q1 = QueryVector(word_lis, all_query[0])
#     q1_freq = q1.query_frequency()
#     q1_idf = q1.idf(docs_freq)
#     q1_tf_idf = q1.query_tf_idf(q1_idf)
#     q_expansion = RocchioQuery(q1_tf_idf, all_result1[i], q1_idf, word_lis)
#     relevant_texts = relevant_text(doc_order, all_doc, relevance)
# #relevant_docs = WordVector(relevance[0], relevant_texts[0], word_lis)
# #relevant_docs_vector = relevant_docs.docs_frequency()
# #relevant_vector = relevant_vector(relevance, relevant_docs_freq)
#     new_q_vector, new_q, length = q_expansion.rocchio(relevant_texts[0], relevance[0], 1)
#     optimal_q_vector.append(new_q_vector)
#     optimal_qlis.append(new_q)
#     optimal_q_length.append(length)
# print(optimal_q_vector[0])
# #print(optimal_q_length)

# # vector space model with new query
# new_result = []
# for i in range(len(optimal_q_vector)):
#     #doc_rank, result = vector_space_model(all_query[i], doc_order, all_doc)
#     q = QueryVector(word_lis, optimal_qlis[i])
#     docs = WordVector(doc_order, all_doc, word_lis)
#     q_idf = q.idf(docs.docs_frequency())
#     docs_tf_idf = docs.docs_tf_idf(q_idf)
#     docs_len = docs.length(docs_tf_idf)
#     ranks = docs_similarity(optimal_q_vector[i], optimal_q_length[i], docs_tf_idf, docs_len)
#     ranks.sort(key=lambda x: x[1], reverse=True)
#     result = []
#     for i in range(len(ranks)):
#         result.append(ranks[i][0])
#     #result, ranks = vsm(optimal_q[i], doc_order, all_doc, word_lis)
#     new_result.append(result)

# query expansion
# new_query = []
# cross_query_cluster = {}
# for i in range(query_number):
#     qe = QueryExpansion(all_query[i], all_result1[0], result_doc_text[0])
#     term_matrix = qe.term_doc_matrix()
#     term_term_matrix = qe.normalized_association_matrix(term_matrix)
#     term_cluster = qe.association_cluster(term_term_matrix)
#     new_query.append(term_cluster)
#     for term in term_cluster:
#         if term not in cross_query_cluster:
#             cross_query_cluster[term] = 1
#         else:
#             cross_query_cluster[term] += 1 

#not use this part
#replicate_term = []
# for key, value in cross_query_cluster.items():
#     if value > 10:
#         replicate_term.append(key)
# for term in replicate_term:
#     for j in range(len(new_query)):
#         if term in new_query[j]:
#             new_query[j].remove(term)

# for i in range(len(new_query)):
#     new_query[i] = all_query[i] + new_query[i] 
#     print("query",i,len(new_query[i]))
 

# after_expansion_result1 = []
# for i in range(len(new_query)):
#     doc_rank, result = vector_space_model(new_query[i], doc_order, all_doc)
#     after_expansion_result1.append(result)

# mAP after query expansion
# total_ap2 = 0
# for i in range(query_number):
#     mAP2 = function.mean_average_precision(new_result[i], relevance[i])
#     total_ap2 += mAP2
# total_map2 = round(total_ap2/query_number, 8)
# map_answer2 = "mAP = " + str(total_map2)
# print("after", map_answer2)
            
print("--- %s seconds ---" % (time.time() - start_time))









