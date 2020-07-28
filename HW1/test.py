import numpy as np
import matplotlib.pyplot as plt
import math
def split_file(file):
    answer = [[]]
    j = 0
    for i in file:
        if i == "\n":
            j += 1
            if j == 16:
                pass
            else:
                answer.append([])
        elif i[:3] == "VOM":
            answer[j].append(i)
    return answer

def calculate(retrieve, order, relevant_number):
    recall = round(retrieve / relevant_number, 4)
    precision = round(retrieve / order, 4)
    #print("order:", order)
    #print("match:", retrieve)
    # if match == len(relevant_set):  # avoid recall is larger than 1
    #     recall = 1
    #print("recall: %f, precision: %f\n" % (recall, precision))
    return recall, precision

def recall_interval(recall):
    return ((recall*10)//1)*10

def compare_interpolate(recall_area):
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
    return final_p, final_r

def mean_average_precision(answer_set, relevant_set):
    order = 0
    retrieve = 0
    sum = 0
    relevant_number = len(relevant_set)
    for i in range(len(answer_set)):
        order += 1
        for j in relevant_set:
            if answer_set[i][:21] == j[:21]: 
                # print("find")
                retrieve += 1
                # print(match, retrieve)
                recall, precision = calculate(retrieve, order, relevant_number)
                r.append(recall)
                p.append(precision)
                sum += precision
                if retrieve > len(relevant_set):
                    break
    # compute the mean average precision
    mean_ap = sum/relevant_number
    #print("map", mean_ap)
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
                # print("find")
                retrieve += 1
                # print(match, retrieve)
                recall, precision = calculate(retrieve, order, relevant_number)
                recall_area[recall_interval(recall)].append((precision, recall))
                r.append(recall)
                p.append(precision)
                if retrieve > len(relevant_set):
                    break
    
    # interpolation of the precision
    for i in recall_area.values():
        i.sort(reverse = True)
    #print(recall_area)
    
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
       
    #print(final_r)
    #print(final_p)

    # plt.plot(final_r, final_p, marker = ".") 
    # plt.xlabel("Recall")
    # plt.ylabel("Precision")  #set y axis to fixed range
    # plt.axis([0,100,0,100])
    #plt.show()

    return final_r, final_p



with open('HW1_ResultsTrainSet.txt', 'r') as answer_set:
    answer = split_file(answer_set)
    # print(len(answer))
    # print(len(answer[2]))

with open('HW1_AssessmentTrainSet.txt', 'r') as relevant_set:
    relevance = split_file(relevant_set)
    # print("relevant file")
    # print(len(relevance))
    # print(len(relevance[4]))

total_precision = {x:[] for x in range(100, -1, -10)}
#total_precision = []
#total_recall = []
for i in range(16):
    r, p = interpolate(answer[i], relevance[i])
    #total_precision.append(p)
    for i in r:
        total_precision[i].append(p[r.index(i)])
    #print(len(total_precision))
    #print(total_precision)


final_precision = []
final_recall = [x for x in range(100, -1, -10)]
for i in total_precision.values():
    sum = 0
    for j in i:
        sum += j
    result = sum/16
    if final_precision != [] and result < final_precision[-1]:
        # interpolate if the max precision is smaller than the larger interval
        final_precision.append(final_precision[-1])
    else:
        final_precision.append(result)

#print(final_precision)
#print(final_recall)
plt.plot(final_recall, final_precision, marker = ".") 
plt.xlabel("Recall")
plt.ylabel("Precision")  #set y axis to fixed range
plt.axis([0,100,0,100])
plt.show()

# calculate map
total_ap = 0
for i in range(16):
    mAP = mean_average_precision(answer[i], relevance[i])
    total_ap += mAP
total_map = round(total_ap/16, 8)
#print("total map:", total_map)

# calculate dcg
# score range is 0-3 and equally distributed among the relevant set
def assign_score(relevant_set):
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
    #print("score:", score)
    return score
    # print(len(score))
    # print(score)
def gain(answer_set, relevant_set, score_list):
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
    # print("num of not 0:", len(rank_list)-c)
    #print(rank_list[:1000])
    # print(len(rank_list))
    return rank_list

def cumulative_gain(rank_list):
    cumulative_set = []
    cumulative_set.append(rank_list[0])
    for i in range(1, len(rank_list)):
        cg = cumulative_set[i-1] + rank_list[i]
        cumulative_set.append(cg)
    # print(len(cumulative_set))
    #print("cg",cumulative_set[:1000])
    return cumulative_set

def discounted_cumulative_gain(rank_list):
    discounted_cg = []
    discounted_cg.append(rank_list[0])
    for i in range(1, len(rank_list)):
        d = rank_list[i]/math.log2(i+1)
        dcg = d + discounted_cg[i-1]
        discounted_cg.append(dcg)
    # print(len(discounted_cg))
    # print("dcg",discounted_cg[:100])
    return discounted_cg

def ideal_dcg(score, answer_set_number):
    ideal_set = score
    added = answer_set_number - len(score)
    ideal_set.extend([0]*added)
    #print("original", ideal_set[:80])
    #print(ideal_set)
    idgc = discounted_cumulative_gain(ideal_set)
    #print(idgc[:80])
    return idgc

def normalized_dcg(query_number, answer_set, relevant_set, score, rank_list):
    total_dcg = []
    total_idcg = []
    for i in range(query_number):
        dcg = discounted_cumulative_gain(rank_list)
        print("dcg", dcg[:10])
        total_dcg.append(dcg)
        idcg = ideal_dcg(score, len(answer_set[i]))
        print("idcg", idcg[:10])
        total_idcg.append(idcg)
        # print(len(total_dgc[i]))
        # print(len(total_idgc[i]))
    
    final_idcg = 0
    final_dcg = 0
    total_ndcg = []
    for i in range(len(answer_set[0])):
        for j in range(query_number):
            # print("i:", i)
            # print("j:", j)
            final_idcg += total_idcg[j][i]
            final_dcg += total_dcg[j][i]
        # final_idcg = final_idcg / query_number
        # final_dcg = final_dcg / query_number
        ndcg = final_dcg / final_idcg
        total_ndcg.append(ndcg)
    # print(total_dgc[0][0])
    # print(total_idgc[0][0])
    #print(total_ndcg[:30])    
    return total_ndcg

score = assign_score(relevance[0])
# print(score)
rank = gain(answer[0], relevance[0], score)
cg = cumulative_gain(rank)
discounted_cumulative_gain(rank)
# print(len(answer[1]))
# print(len(rank))
# ideal_gcd(score, len(answer[0]))
ndcg = normalized_dcg(16, answer, relevance, score, rank)
axis_x = []
for i in range(1, 2266):
    axis_x.append(i)

plt.plot(axis_x, ndcg)
plt.axis([0, 2500, 0 , 1])
plt.show()


    
                




    


