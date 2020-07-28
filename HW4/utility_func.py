import numpy as np
import matplotlib.pyplot as plt
import math


def split_corpus(corpus_file):
    corpus = {}
    for line in corpus_file:
        term = line.split(" ")
        if term[0] == "" in term:
            num = term.count("")
            for i in range(num):
                term.remove("")
        term[-1] = term[-1][:-1]
        # print(term)
        corpus[term[0]] = float(term[1])
    return corpus

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

def split_file(file, query_number):
    """split the file by different queries into seperate list element and return one list as a whole. """
    answer = [[]]
    j = 0
    for i in file:
        if i[0] != "V" and i[0] != "Q":
            j += 1
            if j == query_number:  # answer list only needs to add (query_number - 1) additional empty sublists
                pass
            else:
                answer.append([])
        elif i[:3] == "VOM":
            if i[-1] == "\n":
                i = i[:-1]
            answer[j].append(i)
    return answer

def split_training_file(file, query):
    """split the file by different queries into seperate list element and return one list as a whole. """
    answer = [[]]
    query_name = []
    j = 0
    for i in file:
        if i[0] != "V":
            if i[4:20] in query:
                j += 1
                query_name.append(i[4:20])
                answer.append([])
        elif i[:3] == "VOM":
            if i[-1] == "\n":
                i = i[:-1]
            answer[j].append(i)
    return answer, query_name

def calculate(retrieve, order, relevant_number):
    """Return recall and precision of each found relevant element."""
    recall = round(retrieve / relevant_number, 4)
    precision = round(retrieve / order, 4)
    return recall, precision

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
    if relevant_number != 0:
        mean_ap = sum/relevant_number
    else:
        mean_ap = 0
    return mean_ap

def train_mean_average_precision(query_order, relevant_order, answer_set, relevant_set):
    """calculte mean average precision by summing up all precision and 
    divide the sum by the number of relevant elements."""
    order = 0
    retrieve = 0
    sum = 0
    relevant_number = len(relevant_set)
    for i in range(len(answer_set)):
        if query_order[i] in relevant_order:
            order += 1
            ind = relevant_order.index(query_order[i])
            for j in relevant_set:
                if answer_set[i][:21] == j[:21]: 
                    retrieve += 1
                    recall, precision = calculate(retrieve, order, relevant_number)
                    sum += precision
                    if retrieve > len(relevant_set):
                        break
    # compute the mean average precision
    if relevant_number != 0:
        mean_ap = sum/relevant_number
    else:
        mean_ap = 0
    return mean_ap