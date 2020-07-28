import numpy as np
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Cm
import math

def split_file(file):
    """split the file by different queries into seperate list element and return one list as a whole. """
    answer = [[]]
    j = 0
    for i in file:
        if i == "\n":
            j += 1
            if j == 16:  # answer list only needs to add 15 additional empty sublists
                pass
            else:
                answer.append([])
        elif i[:3] == "VOM":
            answer[j].append(i)
    return answer

def remove_newline_symbol(file_lis):
    for i in range(len(file_lis)):
        for j in range(len(file_lis[i])):
            end = len(file_lis[i][j]) - 1
            if file_lis[i][j][end:] == "\n":
                #print("in if")
                file_lis[i][j] = file_lis[i][j][:-1]
    


def calculate(retrieve, order, relevant_number):
    """Return recall and precision of each found relevant element."""
    recall = round(retrieve / relevant_number, 4)
    precision = round(retrieve / order, 4)
    return recall, precision

def recall_interval(recall):
    """Return the interval of recall classified to 11 equal intervals of 10 (the field range is 0-100)"""
    return ((recall*10)//1)*10

def compare_interpolate(recall_area):
    """
    o the interpolation within each interval and beyond accoording to the function.
    Return the lists of precisions and interpolated recalls.
    """
    final_r = []
    final_p = []
    for i in range(100, -1, -10):
        final_r.append(i)
        if recall_area[i] != []:
            # interpolate if the max precision is smaller than the larger interval
            if i != 100 and recall_area[i][0][0]*100 < final_p[-1]:
                final_p.append(final_p[-1])
            else:
                final_p.append(recall_area[i][0][0]*100)
        # if no precision is in the interval, use the precision of larger interval
        else:
            final_p.append(final_p[-1])
    return final_p, final_r

def mean_average_precision(answer_set, relevant_set):
    """calculte mean average precision by summing up all precision and 
    divide the sum by the number of relevant elements."""
    order = 0
    retrieve = 0
    sum = 0
    relevant_number = len(relevant_set)
    for i in range(len(answer_set)):
        order += 1
        for j in relevant_set:
            if answer_set[i][:21] == j[:21]: 
                retrieve += 1
                recall, precision = calculate(retrieve, order, relevant_number)
                sum += precision
                if retrieve > len(relevant_set):
                    break
    # compute the mean average precision
    mean_ap = sum/relevant_number
    return mean_ap



def interpolate(answer_set, relevant_set):
    order = 0
    retrieve = 0
    recall_area = {0:[], 10:[], 20:[], 30:[], 40:[], 50:[], 60:[], 70:[], 80:[], 90:[], 100:[]}
    r = []
    p = []
    relevant_number = len(relevant_set)
    for i in range(len(answer_set)):
        order += 1
        for j in relevant_set:
            if answer_set[i][:21] == j[:21]: 
                retrieve += 1
                recall, precision = calculate(retrieve, order, relevant_number)
                recall_area[recall_interval(recall)].append((precision, recall))
                r.append(recall)
                p.append(precision)
                if retrieve > len(relevant_set):
                    break
    
    # interpolation of the precision
    for i in recall_area.values():
        i.sort(reverse = True)
    
    final_p, final_r = compare_interpolate(recall_area)
    final_r = []
    final_p = []
    for i in range(100, -1, -10):
        final_r.append(i)
        if recall_area[i] != []:
            if i != 100 and recall_area[i][0][0]*100 < final_p[-1]:
                # interpolate if the max precision is smaller than the larger interval
                final_p.append(final_p[-1])
            else:
                final_p.append(recall_area[i][0][0]*100)
        else:
            # if no precision is in the interval, use the precision of larger interval
            final_p.append(final_p[-1])

    return final_r, final_p

def assign_score(relevant_set):
    """Assign score to each relevant element in descending order and return the score list."""
    section = len(relevance[0])//3
    score = []
    s = 3
    for i in range(3):
        if s == 1:
            num = len(relevance[0]) - len(score)
            score.extend([s]*num)
        else:
            score.extend([s]*section)
            s -= 1
    return score

def gain(answer_set, relevant_set, score_list):
    """Form a score list based on the answer set and return the rank list."""
    rank_list = []
    order_list = []
    for i in range(len(answer_set)):
        item = answer_set[i][:21] + "\n"
        if item in relevant_set:
            rank_list.append(score_list[relevant_set.index(item)])
            order_list.append(item)
        else:
            rank_list.append(0)
            order_list.append("no")
    c = rank_list.count(0)
    return rank_list

def cumulative_gain(rank_list):
    """Calculate the cumulative gain based on the rank list and return a list."""
    cumulative_set = []
    cumulative_set.append(rank_list[0])
    for i in range(1, len(rank_list)):
        cg = cumulative_set[i-1] + rank_list[i]
        cumulative_set.append(cg)
    return cumulative_set

def discounted_cumulative_gain(rank_list):
    """Calculate the discounted cumulative gain based on the input rank list and return a list."""
    discounted_cg = []
    discounted_cg.append(rank_list[0])
    for i in range(1, len(rank_list)):
        d = rank_list[i]/math.log2(i+1)
        dcg = d + discounted_cg[i-1]
        discounted_cg.append(dcg)
    return discounted_cg

def ideal_dcg(score, answer_set_number):
    """Calculate the ideal discounted cumulative gain based on a descending rank list and return a list."""
    ideal_set = score
    added = answer_set_number - len(score)
    ideal_set.extend([0]*added)
    idgc = discounted_cumulative_gain(ideal_set)
    return idgc

def normalized_dcg(query_number, answer_set, relevant_set, score, rank_list):
    """Calculate normalized discounted cumulative gain of various queries and return a list."""
    total_dcg = []
    total_idcg = []
    for i in range(query_number):
        dcg = discounted_cumulative_gain(rank_list)
        total_dcg.append(dcg)
        idcg = ideal_dcg(score, len(answer_set[i]))
        total_idcg.append(idcg)
    
    final_idcg = 0
    final_dcg = 0
    total_ndcg = []
    for i in range(len(answer_set[0])):
        for j in range(query_number):
            final_idcg += total_idcg[j][i]
            final_dcg += total_dcg[j][i]
        ndcg = final_dcg / final_idcg
        total_ndcg.append(ndcg)  
    return total_ndcg