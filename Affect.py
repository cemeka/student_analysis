"""
Script to categorize tags into one of three sentiment groups: positive, negative, neutral, and
then (1) compare the means of the three groups and (2) compare the distribution of the groups for the questions asked. 
"""



import csv
import statistics
import scipy.stats as stats
from collections import defaultdict
import pandas as pd
import chisquareindtest


def get_affect_leaning(groupings, list_of_sentiments):
    """
    Function which returns prevailing sentiment of student regarding the exam. 
    The functions takes info about how to classify tags, as well as a list of tags to classify, as input. 
    """
    neut = []
    pos = 0
    neg = 0
    neutral = 0
    for sentiment in list_of_sentiments:
        #sentiment = sentiment.replace(" ", "")
        sentiment = sentiment.upper()
        if sentiment in groupings["positive"]:
            pos += 1
        elif sentiment in groupings["negative"]:
            neg += 1
        else:
            neutral += 1
            neut.append(sentiment)
    return decision_boundary(pos, neg, neutral, "only")

#TODO: [Maybe expand so that we can also handle a numerical boundary e.g 60%]
def decision_boundary(pos, neg, neutral, boundary):
    if boundary == "majority":
        if pos > neg and pos >= neutral:
            return "positive"
        if neg > pos and neg >= neutral:
            return "negative"
        if neutral > pos and neutral > neg:
            return "neutral"
        
        
    #changed so that neutral means that number positive == number negative.
    #discarding students with mixed views as well. 
    if boundary == "only":
        if pos > 0 and neg == 0:
            return "positive"
        if pos == 0 and neg > 0:
            return "negative"
        if pos == 0 and neg == 0:
            return "neutral"
        return "mixed"

    if type(boundary) == int:
        per_pos = pos / (pos + neg + neutral)
        per_neg = neg / (pos + neg + neutral)
        per_neutral = neutral / (pos + neg + neutral)

        if per_pos > boundary and per_pos > per_neg and per_pos > per_neutral:
            return "positive"
        if per_neg > boundary and per_neg > per_pos and per_neg > per_neutral:
            return "negative"
        if per_neutral > boundary and per_neutral > per_pos and per_neutral > per_neg:
            return "neutral"
        
        
    return "tie"
    
def display_affect_leanings(question_variants):
    """
    Given a dictionary, which contains {question variant: list} key-value pairs, 
    for each list, return the count of positive, negative and neutral effects for that list
    """
    print("Question Variant, Pos, Neg, Neutral, Mixed")
    variant_dists = []
    for question in question_variants:
        if question is None or len(question.strip()) == 0:
            continue
            
        pos = 0
        neg = 0
        neutral = 0
        mixed = 0
        for sentiment in question_variants[question]:
            if sentiment == "positive":
                pos += 1
            elif sentiment == "negative":
                neg += 1
            elif sentiment == "neutral":
                neutral += 1
            else:
                mixed += 1
                #print("undecided1: {}".format(sentiment))
        print("{}, {}, {}, {} ,{}".format(question, pos, neg, neutral, mixed))
        variant_dists.append([pos, neg, neutral, mixed])
    return variant_dists

def get_comments(row1):
    """
       clean up data to get student comments. 
    """
    comments = []
    row1 = row1.split(";")
    for comment in row1:
        comment = comment.replace(" ", "").upper()
        if len(comment) == 0 :
            continue
        comments.append(comment)
    return comments
    


students = {}
q1 = defaultdict(list)
q2 = defaultdict(list)

affect_points = defaultdict(list)

neutral_marked = []


golden_sentiment_groups = {}
# =============================================================================
#original sentiment groups before paper submission deadline
# golden_sentiment_groups["positive"] =["ES", "EF", "DQPC", "DQPC?", "ASYNC+", "PEPC", "PEMF", "PEME", "COMPLEX", "RA", "CENTRALLIMIT", "TIMEOK", "FAIRGAME", "GENOK"] 
# golden_sentiment_groups["negative"] = ["UNFAIR", "DQUF", "PE->C", "PTS", "MSD", "MORESIMILAR", "NS", "NI", "PP", "VB", "DOBETTER", "VERSIONANX", "MORESMALLER", "VARTOOBIG", "PREEXAMVAR", "TIME", "EXAMUNCLEAR", "IGOTLUCKY", "UNLUCKY", "HQL"]
# 
# =============================================================================


golden_sentiment_groups["positive"] =["ES", "EF", "DQPC", "DQPC?", "ASYNC+", "PEPC", "PEMF", "PEME", "COMPLEX", "RA", "CENTRALLIMIT", "TIMEOK", "FAIRGAME", "GENOK"] 
golden_sentiment_groups["negative"] = ["UNFAIR", "DQUF", "MORESIMILAR", "PP", "VB", "DOBETTER", "VERSIONANX", "MORESMALLER", "VARTOOBIG", "PREEXAMVAR", "TIME", "IGOTLUCKY", "UNLUCKY", "HQL"]

with open('FairnessDataWithTagsNumbers.csv', encoding = "utf-8") as csv_file:
    #TODO: need to remove first line of file: file headers
    csv_reader = csv.reader(csv_file, delimiter=',')
    i = 0
    next(csv_reader)
    for row in csv_reader:
        student_id = row[0]
        student_score = float(row[10])
        
        student_comments = get_comments(row[7]) + get_comments(row[8]) + get_comments(row[9])
        #print the student number and their comments
        #print("{}, ->{}<-".format(i, student_comments))
        i = i + 1
        affect = get_affect_leaning(golden_sentiment_groups, student_comments)
        students[student_id] = affect

        
        question_1_variant = row[11]
        question_2_variant = row[14]
        q1[question_1_variant].append(affect)
        q2[question_2_variant].append(affect)

        affect_points[affect].append(student_score)

#display leanings of students for each question, then run data analysis.
print("DISTRIBUTION OF TAGS BY SENTIMENT & HYPOTHESIS TESTING\n")
q1_results = display_affect_leanings(q1)
q1_df = pd.DataFrame(q1_results, columns = ["Positive", "Negative", "Neutral", "Mixed"])
chisquareindtest.chisq_and_posthoc_corrected(q1_df)
print("------------------")

q2_results = display_affect_leanings(q2)
q2_df = pd.DataFrame(q2_results, columns = ["Positive", "Negative", "Neutral", "Mixed"])
chisquareindtest.chisq_and_posthoc_corrected(q2_df)
print("\n\n------------------")



##manually generated data used for testing purposes.
#test_data = [[92, 100, 94, 80], [65, 73, 85, 90], [70, 69, 80, 99], [98, 98, 97, 90], [80, 85, 85, 85]]
#test_df = pd.DataFrame(test_data, columns = ["Positive", "Negative", "Neutral", "Other"])
#chisquareindtest.chisq_and_posthoc_corrected(test_df)
#print("\n\n------------------")



#using this line to drop a group of categories where a student expressed various sentiments (e.g. some positive or negative)
#del affect_points["disposed"]

print("COMPARISONS OF AVERAGE POINTS BY SENTIMENT\n")

for category in affect_points:
    minV = min(affect_points[category])
    maxV = max(affect_points[category])
    meanV = statistics.mean(affect_points[category])
    stdevV = statistics.pstdev(affect_points[category])
    countV = len(affect_points[category])
    print("Category: {}, mean: {}, st dev: {}, min: {}, max: {}, count: {}\n".format(category, meanV, stdevV, minV, maxV, countV))

#we run one-way ANOVA on the three groups (pos, neg, neutral)

print("Omnibus test for difference of means: ", end = "")
print(stats.f_oneway(affect_points["positive"], affect_points["negative"], affect_points["neutral"], affect_points["mixed"]))
print()
print("Positive vs Negative:")
print(stats.f_oneway(affect_points["positive"], affect_points["negative"]))
print()
print("Positive vs Mixed:")
print(stats.f_oneway(affect_points["positive"], affect_points["mixed"]))
print()
print("Positive vs Neutral:")
print(stats.f_oneway(affect_points["positive"], affect_points["neutral"]))
print()
print("Mixed vs Neutral:")
print(stats.f_oneway(affect_points["mixed"], affect_points["neutral"]))
print()
print("Neutral vs Negative:")
print(stats.f_oneway(affect_points["neutral"], affect_points["negative"]))
print()
print("Mixed vs Negative:")
print(stats.f_oneway(affect_points["mixed"], affect_points["negative"]))
