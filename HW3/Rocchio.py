import numpy as np
from numpy import inf
from search_system import *
from system_evaluation import *

class RocchioQuery:
    def __init__(self, one_query_frequency_dict, docs_ranking_order, idf, word_collection):
        self.query_frequency = one_query_frequency_dict
        self.collection = word_collection
        self.idf = idf
        self.docs_ranking_order = docs_ranking_order
    
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

        # obtain the tf-idf of the relevant docs
        relevant_docs = WordVector(pick_doc_list, pick_texts, self.collection)
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
        #print("score", score_rank)
        final_rele_vector = {}
        count = 0
        total = 230
        for i in range(total):
            if i > (len(score_rank) - 1):
                break
            if score_rank[i][0] not in new_query_freq.keys():
                final_rele_vector[score_rank[i][0]] = score_rank[i][1] 


        # compute adjusted query tf_idf by mutiplying original query with a
        for term in new_query_freq.keys():
            new_query_freq[term] *= a 

        # calculate standard Rocchio
        for term, freq in final_rele_vector.items():
            if term in new_query_freq.keys():
                new_query_freq[term] += freq * (b / total_relevant)
            else:
                new_query_freq[term] = freq * (b / total_relevant)

        # calculate length of new query
        total = 0
        for term, freq in new_query_freq.items():
            total += freq ** 2
        length = math.sqrt(total)

        # make a list of new query
        new_q = list(new_query_freq.keys())
        
        return new_query_freq, new_q, length





            




