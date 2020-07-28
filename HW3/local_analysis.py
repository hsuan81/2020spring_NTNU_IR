import numpy as np
from numpy import inf
from search_system import *
from system_evaluation import *

class QueryExpansion:
    def __init__(self, origin_query, search_result: list, doc_text: list):
        self.origin_query = origin_query
        self.doc_set = search_result[:2]
        self.doc_text = doc_text[:2]
        t = []
        for i in range(len(self.doc_set)):
            for j in self.doc_text[i]:
                if j not in t:
                    t.append(j)
        self.terms = origin_query + t
        self.term_amount = len(self.terms)

    
    def term_doc_matrix(self):
        term_doc_matrix = np.zeros((len(self.terms), len(self.doc_set)), dtype = np.int)
        for i in range(len(self.terms)):
            term = self.terms[i]
            for j in range(len(self.doc_text)):
                text = self.doc_text[j]
                if term in text:
                    term_doc_matrix[i][j] += text.count(term)
        return term_doc_matrix

    def association_matrix(self, term_doc_matrix):
        transpose_m = np.transpose(term_doc_matrix)
        return np.dot(term_doc_matrix, transpose_m)
    
    def normalized_association_matrix(self, term_doc_matrix):
        transpose_m = np.transpose(term_doc_matrix)
        association_m = np.dot(term_doc_matrix, transpose_m)
        #normalized_m = association_m
        urow_m = []
        for i in range(self.term_amount):
            row = [association_m[i, i]] * self.term_amount
            urow_m.append(row)
        urow_in_np = np.array(urow_m, dtype=float)
        ucol_in_np = np.transpose(urow_in_np)
        divisor_m = np.reciprocal(np.add(urow_in_np, ucol_in_np))
        divisor_m[divisor_m == inf] = 0
        normalized_m = np.multiply(association_m, 2) * divisor_m
        

        # for i in range(len(self.terms)):
        #     for j in range(len(self.terms)):
        #         #print(association_m[i][i], association_m[j][j])
        #         if association_m[i,i] == 0 and association_m[j,j] == 0:
        #             normalized_m[i,j] = 0
        #         else:
        #             normalized_m[i,j] = association_m[i,j]/(association_m[i,i] + association_m[j,j])
        return normalized_m 

    def association_cluster(self, association_matrix):
        index = len(self.origin_query)
        #print("index",index)
        cluster = []
        # look for other terms relevant to the query
        for i in range(0, index):
            terms_set = []
            for j in range(index, len(self.terms)):
                terms_set.append([self.terms[j] ,association_matrix[i][j]])
                #print(terms_set)
            terms_set.sort(key=lambda x: x[1], reverse=True)
            #print(len(terms_set))
            # pick out the top m terms and remove crossing query terms
            
            for k in range(10):
                if terms_set[k][0] not in cluster:
                    cluster.append(terms_set[k][0])
           
        return cluster

class RocchioQuery:
    def __init__(self, one_query_frequency_dict, docs_ranking_order, idf, word_collection):
        self.query_frequency = one_query_frequency_dict
        self.collection = word_collection
        self.idf = idf
        self.docs_ranking_order = docs_ranking_order
        # for q in Query:
        #     if q not in self.query:
        #         self.query[q] = 1
        #     else:
        #         self.quer[q] += 1
    
    def get_k_top_relevant(self, k, relevant_texts: list, relevant_docs_list: list):
        k_top_rele = []
        k_top_texts = []
        i = 0
        while len(k_top_rele) < k:
            if len(relevant_docs_list) < k:
                k_top_texts = relevant_texts
                k_top_rele = relevant_docs_list
                break
            if self.docs_ranking_order[i] in relevant_docs_list:
                k_top_rele.append(self.docs_ranking_order[i])
                index = relevant_docs_list.index(self.docs_ranking_order[i])
                k_top_texts.append(relevant_texts[index])
            i += 1
        return k_top_rele, k_top_texts

    def rocchio(self, relevant_texts: list, relevant_docs_list: list, top_k: int):
        """
        Argument: 
            relevent_texts: [['2280', '4432'], ['3444',...]]
            relevant_docs_list: ['VOM19981004.1919.2257', 'VOM19990823.8899.1100',...]
            top_k: one integer

        Return:
            new_query_freq: {'term1': 2.99944, 'term2': 2.4458,... }
            new_q: ['term1', 'term2', ...]
            length: one float
        """
            
        a, b, c = 1, 1, 0
        new_query_freq = self.query_frequency
        # pick the top x relevant docs
        pick_doc_list, pick_texts = self.get_k_top_relevant(top_k, relevant_texts, relevant_docs_list)
        # x = k
        # if len(relevant_docs_list) < x:
        #     pick_doc_list = relevant_docs_list
        #     pick_texts = relevant_texts
        # else:
        #     pick_doc_list = relevant_docs_list[:x]
        #     pick_texts = relevant_texts[:x]

        # obtain the tf-idf of the relevant docs
        relevant_docs = WordVector(pick_doc_list, pick_texts, self.collection)
        #relevant_freq = relevant_docs.docs_frequency()
        relevant_tf_idf = relevant_docs.docs_tf_idf(self.idf)
        total_relevant = len(relevant_docs_list)
        # calculate word vector of all relevant docs
        relevant_vector = {}
        for doc, freq in relevant_tf_idf.items():
            for term, num in freq.items():
                if term in relevant_tf_idf.keys():
                    relevant_vector[term] += freq[term]
                else:
                    relevant_vector[term] = freq[term]
        
        # pick top x tf-idf terms
        score_rank = [[k, v] for k, v in sorted(relevant_vector.items(), key=lambda item: item[1], reverse=True)]
        print("score", score_rank)
        final_rele_vector = {}
        count = 0
        total = 230
        for i in range(total):
            if i > (len(score_rank) - 1):
                break
            if score_rank[i][0] not in new_query_freq.keys():
                final_rele_vector[score_rank[i][0]] = score_rank[i][1]
    
        # for term, freq in score_rank.items():
        #     if count < total and term not in new_query_freq.keys():
        #         final_rele_vector[term] = freq
        #         count += 1
        #     else:
        #         break   


        # compute adjusted query tf_idf by mutiplying original query with a
        for term in new_query_freq.keys():
            new_query_freq[term] *= a 

        # calculate standard Rocchio
        for term, freq in final_rele_vector.items():
            if term in new_query_freq.keys():
                new_query_freq[term] += freq * (b / total_relevant)
            else:
                new_query_freq[term] = freq * (b / total_relevant)
        #new_q_vector = list(new_query_freq.keys())
        #for term in new_query_freq.keys():
        #    count = new_query_freq[term]
        #    new_q.extend([term] * count)

        # calculate length of new query
        total = 0
        for term, freq in new_query_freq.items():
            total += freq ** 2
        length = math.sqrt(total)

        # make a list of new query
        new_q = list(new_query_freq.keys())
        
        return new_query_freq, new_q, length





            




