
#Also, look up multi-level index in pandas. what is a dataframe with multilevel index: print tag_df
#TODO: Need to do appropriate hypothesis testing for various data we have generated. 
#TODO: Revisit section HARD. tag_df, zilles_tags_df and chinny_tags_df can be simplied with a function. 



# -*- coding: utf-8 -*-
"""
Created on Mon Sep 2 08:31:08 2019

@author: Chinedu
"""



#Exploding row into columns
#https://stackoverflow.com/questions/12680754/split-explode-pandas-dataframe-string-entry-to-separate-rows

#Building co-occurence matrix. 
#https://stackoverflow.com/questions/31518937/convert-two-column-data-frame-to-occurrence-matrix-in-pandas?rq=1


#Using apply and lambdas in panda
#Very good link: https://towardsdatascience.com/apply-and-lambda-usage-in-pandas-b13a1ea037f7


#can convert into ones and zeros.
import statistics
import pandas as pd



def tidy_split(df, column, sep='|', keep=False):
    """
    Split the values of a column and expand so the new DataFrame has one split
    value per row. Filters rows where the column is missing.

    Params
    ------
    df : pandas.DataFrame
        dataframe with the column to split and expand
    column : str
        the column to split and expand
    sep : str
        the string used to split the column's values
    keep : bool
        whether to retain the presplit value as it's own row

    Returns
    -------
    pandas.DataFrame
        Returns a dataframe with the same columns as `df`.
    """
    indexes = list()
    new_values = list()
    #df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    return new_df

def determine_question_difficulty(hard, easy, value):
    """
    Returns a value denoting difficulty of a question assigned by researcher. 
    """
    if value in easy:
        return "EASY"
    elif value in hard:
        return "HARD"
    else:
        return "NEUTRAL"


def determine_theme_group(tag, theme_dict):
    for theme_name in theme_dict:
        for cur_tag  in theme_dict[theme_name]:
            if tag == cur_tag:
                return theme_name
    return tag


def categorize_unfair(tag, listOfUnfair):
    if tag == None or len(tag) == 0:
        return tag
    elif tag.upper() in listOfUnfair:
        return "NOTFAIR"
    else:
        return tag
    

fileLocation = "FairnessDataWithTagsNumbers.csv"

df = pd.read_csv(fileLocation)

original_df_copy = df.copy()


#-------------------------------------------------------------------
#Initial analysis is to compare average for students who filled out survey against those who did. 
#TODO: maybe show 5 number summary of students who took vs didn't take the exam. 
#all students who took the survey.
students_scores_with_survey = sorted(df["points"].tolist()) 

print("range = {a} to {b}".format(a = students_scores_with_survey[0], b = students_scores_with_survey[-1] ) )
#all students in class
all_students_scores_df = pd.read_csv("overall_grade_distribution.csv") 

all_students_scores = all_students_scores_df["TotalWithoutEC"].tolist()

#figure out the points of students who didn't take survey. list not in order.
students_without_survey = sorted(list(set(all_students_scores) - set(students_scores_with_survey)))

#print("Avg score of students who completed survey = {}".format(statistics.mean(students_scores_with_survey)))

#print("Avg score of students who didn't complete survey = {}".format(statistics.mean(students_without_survey)))

for score in students_without_survey:
    print(round(score, 2))


#--------------------------------------------------------------------

# =============================================================================
# Building co-occurence matrix in pandas.
# #https://pbpython.com/pandas-crosstab.html
# #for marginal probabilities on row, use normalize = "index".
# #for marginal prob. on column, use normalize = "columns"
# 
# pd.crosstab(df.q1, df.q2, margins=True, normalize="index").to_csv("QuestionCooccurenceMarginalProportions.csv")
#  
# 
# =============================================================================

#Co-occurence matrix for question 1 and question 2. 

#before splitting up the data to make flat file
#compute raw counts of occurences.  
pd.crosstab(df.q1, df.q2, margins=True).to_csv("Question Cooccurrence Counts.csv")

#compute and save co-occurence percentages of q1 and q2.
#each cell should ideally have equal values.
pd.crosstab(df.q1, df.q2, margins=True, normalize=True).to_csv("Question Cooccurrence Proportions.csv")
 

#--------------------------------------------------------------------------------------------

#Summary statistics per tag.

#need to split preexamtags, securitytags and variancetags. 
df = tidy_split(df, "PreExamTags", sep=";").dropna(subset=["PreExamTags"])
df = tidy_split(df, "SecurityTags", sep=";").dropna(subset=["SecurityTags", "PreExamTags"])
df = tidy_split(df, "VarianceTags", sep=";").dropna(subset=["VarianceTags", "SecurityTags", "PreExamTags"])






df["PreExamTags"]= df["PreExamTags"].str.strip().str.upper()
df["SecurityTags"] = df["SecurityTags"].str.strip().str.upper()
df["VarianceTags"] = df["VarianceTags"].str.strip().str.upper()





#pivot the data such that the 3 columns (preexam, variance and security)  are re-organized into multiple rows where we have just one tag on each row 
#if we want to include the tag dimesion (e.g. "preexamtags" or "variancetags"), we neeed to remove the drop statement. 
reformatted_df = pd.melt(df, id_vars=["StudentID", "points", "q1", "q2"], value_vars=["PreExamTags", "VarianceTags", "SecurityTags"], var_name="QuestionCategory", value_name="Tag")
reformatted_df = reformatted_df.drop(columns=["QuestionCategory"]).drop_duplicates().sort_values('StudentID').reset_index(drop=True)


#assuming that NAN is value used to represent that data is missing. 
reformatted_df = reformatted_df[reformatted_df.Tag != "NAN"]



#TODO: drop columns where we don't have data. already handled: confirm and remove comment
#reformatted_df =  reformatted_df.dropna(subset = ["Tag"]) 


#pandas aggregation reference: http://queirozf.com/entries/pandas-dataframe-groupby-examples=
#.apply(lambda x: x/x.sum())


tag_df = reformatted_df.groupby("Tag")["points"].agg(
         {
             "points": ["mean", "min", "max", "median"],
              "Tag": ["count"]
         }         
         )
tag_df["tag_proportion"] = tag_df["Tag"]["count"]/tag_df["Tag"]["count"].sum()

tag_df.to_csv("Data Summary For Tags10.csv")

#-------------------------------------------------------------------------------------
#Summary statistics per question.
#Note that we're using the original dataframe to avoid overcounting. 
q1_data_df = original_df_copy.groupby("q1")["points"].agg({
             "points": ["mean", "min", "max", "median", "std"],
              "q1": ["count"]
         } )

q2_data_df = original_df_copy.groupby("q2")["points"].agg({
             "points": ["mean", "min", "max", "median", "std"],
              "q2": ["count"]
         } )


q1_data_df.to_csv("Point Distribution For  Question 1 Variants.csv")
q2_data_df.to_csv("Point Distribution For Question 2 Variants.csv")
#-------------------------------------------------------------------------------------

#SECTION HARD vs EASY tags
#compute summary stats for "hard" tags, "easy" tags

#selecting only particular rows python: https://cmdlinetips.com/2018/02/how-to-subset-pandas-dataframe-based-on-values-of-a-column/

#try changing the values in the two arrays to special keys that we can then use to group by.
#print(reformatted_df)
#print(reformatted_df.columns)
zilles_hard = ["UNFAIR", "CURVE", "DQNN", "DQUF", "MORESIMILAR", "PP", "VB", "DOBETTER", "HARD", "VERSIONANX", "UNDERSTUDIED", "EXAMDIFFHW", "VARTOOBIG", "TIME", "UNLUCKY", "GENOK", "RELEASESTATS" ]
zilles_easy = ["EF", "DQPC?", "ASYNC+", "PE->C", "PEME", "PTS", "MSD", "COMPLEX", "STUDYALL", "WORKMORE", "CPL", "NOIMPACT", "ENOUGHTIME", "UNWANTED", "NOTHARD", "CENTRALLIMIT", "TIMEOK", "FAIRGAME", "IGOTLUCKY"]

zilles_tags_df = reformatted_df.copy()
zilles_tags_df["Tag"] = reformatted_df["Tag"].apply(lambda x: determine_question_difficulty(zilles_hard, zilles_easy, x))
zilles_tags_df = zilles_tags_df.drop_duplicates().groupby("Tag")["points"].agg(
         {
             "points": ["mean", "min", "max", "median", "std"],
              "Tag": ["count"]
         }         
         )
zilles_tags_df.to_csv("Difficulty Data for Zilles Tags.csv")


#print(zilles_tags)

chinny_hard = ["UNDERSTUDIED", "UNDERPREPARED", "MEMORIZED", "ES", "PIH", "COMM", "PELH", "EARLIER", "MORE", "PRACTICE", "VB", "MORESIMILAR", \
               "UNLUCKY", "EXAMDIFFHW", "COVERAGE", "HARD", "EXAMUNCLEAR", "VARTOOBIG", "UNFAIR", "DOBETTER", "DQNN", "COMPLEX", "DQUF", "DEBUG", "PARTIAL", "RETAKE", "CURVE"]
chinny_easy = ["IGOTLUCKY", "NOTHARD", "PEME", "PTS", "MSD", "NS"]
chinny_tags_df = reformatted_df.copy()
chinny_tags_df["Tag"] = reformatted_df["Tag"].apply(lambda x: determine_question_difficulty(chinny_hard, chinny_easy, x))
chinny_tags_df = chinny_tags_df.drop_duplicates().groupby("Tag")["points"].agg(
         {
             "points": ["mean", "min", "max", "median", "std"],
              "Tag": ["count"]
         }         
         )
chinny_tags_df.to_csv("Difficulty Data for Chinny Tags.csv")



#-------------------------------------------------------------------------------------


#SECTION Zilles and Chinny themes
zilles_themes = {}
zilles_themes["exam_related"] = ["MORE", "PRACTICE", "HARD", "NOT HARD", "EXAMDIFFHW", "EXAM UNCLEAR", "UNCLEAR", "FLEXIBILITY", "COVERAGE", "DEBUG", "MORE TIME", "TIMEOK"]
zilles_themes["transparency_related"] = ["POSTEXAMREVIEW", "RELEASE STATS", "DIST"]
zilles_themes["variation_problematic"] = ["UNFAIR", "VB", "DQUF", "PP", "VERSION ANX", "DOBETTER", "TIME", "I GOT LUCKY", "UNLUCKY", "VARTOOBIG", "PREEXAMVAR"]
zilles_themes["student_suggestions_improvement"] = ["CURVE", "MORE SIMILAR", "RETAKE", "CHOICE", "HQL", "PARTIAL", "MORE SMALLER", "NARROW"]
zilles_themes["exams_fair"] = ["EF", "GENOK", "CENTRALLIMIT","CENTRAL LIMIT", "FAIR GAME"]
zilles_themes["exams_secure_no_cheating"] = ["ES", "DQPC", "DQPC?", "COMPLEX", "MEMORIZED", "PEPC"]
zilles_themes["not_secure_enough"] = ["NS", "NI", "PTS", "MSD", "CHEATERSWILLWIN", "COMM", "CHEATERS WILL FIND A WAY"]
zilles_themes["learning_related"] = ["DQ->STUDYMORE", "STUDY ALL", "CPL", "LEARNING", "CHEATING PREVENTS LEARNING"]
zilles_themes["preexam_good"] = ["PEMF", "PEME", "WORKMORE","WORK MORE","ENOUGH TIME","ENOUGHTIME", "GS", "RA", "HELP", "HELPFUL", "DEPTH" , "EARLIER->EF", "NO PROCRASTINATE"]
zilles_themes["preexam_neutral"] = ["EFFICIENT", "PELH", "NO IMPACT"]
zilles_themes["preexam_negative_affect"] = ["EARLIER", "MISLEADING", "NOT USEFUL", "PE->C", "UNWANTED"]
zilles_themes["people_failure_own_fault"] = ["UNDERPREPARED", "UNDERSTUDIED"]
zilles_themes["suprising_contradictory_student_opinions"] = ["OBJECTIVE", "PEOPLEVAR", "DQNN", "ES!=ED"]

zilles_themes_df = reformatted_df.copy()
zilles_themes_df["Tag"] = reformatted_df["Tag"].apply(lambda x: determine_theme_group(x, zilles_themes))

zilles_themes_df = zilles_themes_df.drop_duplicates().groupby("Tag")["points"].agg(
         {
             "points": ["mean", "min", "max", "median", "std"],
              "Tag": ["count"]
         }         
         )
zilles_themes_df.to_csv("Point Distribution for Zilles Themes.csv")







chinny_themes = {}


chinny_themes["people_luck"] = ["PEOPLEVAR", "IGOTLUCKY", "I GOT LUCKY", "NOTHARD", "NOT HARD"]
 
chinny_themes["unprepared"] = ["UNDERSTUDIED","UNDERPREPARED", "MEMORIZED"]
 
chinny_themes["preexam_helpful"] = ["GS", "DEPTH", "RA", "HELP", "HELPFUL", "STUDYALL", "STUDY ALL", "WORKMORE", "WORK MORE","EFFICIENT", "NOPROCRASTINATE", "NO PROCRASTINATE"]
 
chinny_themes["preexam_makes_fair"]= ["PEMF", "EARLIER->EF", "PEME", "ENOUGHTIME", "CENTRALLIMIT", "OBJECTIVE", "TIMEOK", "PEPC", "PRE-EXAM->FAIR"]
 
chinny_themes["exam_fair"] = ["EF", "GENOK", "DQPC", "ES", "PIH", "DQPC?", "ASYNC+"]
 
chinny_themes["exam_unsecure"] = ["PE->C","UNWANTED", "PTS", "MSD", "CHEATERSWILLWIN","CPL", "NS", "NI", "COMM"]
 
chinny_themes["needs_major_improvement"] = ["PELH","EARLIER", "MORE", "PRACTICE", "VB", "MORESIMILAR","MORE SIMILAR", "UNLUCKY", "VERSIONANX", "VERSION ANX","EXAMDIFFHW", "COVERAGE", "HARD", "EXAM UNCLEAR", "UNCLEAR", "VARTOOBIG", "PREXAMVAR", "UNFAIR", "DOBETTER"]
 
chinny_themes["traditional_prefered"] = ["DQNN", "COMPLEX" ,"PP", "NARROW", "DQUF","NOT USEFUL","NOIMPACT", "NO IMPACT", "MISLEADING", "PREEXAMVAR", "TRICK->UNFAIR"]
 
chinny_themes["more_tools_needed"] = ["DEBUG", "MORETIME", "MORE TIME" ,"CHOICE", "FLEXIBILITY", "PARTIAL", "RETAKE", "CURVE","TIME", "MORESMALLER", "MORE SMALLER"]
 
#maximize_knowledge_gain captures idea that students presumably want to learn as much as possible; they also want to see exam afterwards. 
chinny_themes["maximize_knowledge_gain"] = ["LEARNING", "FAIRGAME", "FAIR GAME", "DQ->STUDYMORE", "RELEASE STATS" ,"RELEASESTATS","DIST", "POSTEXAMREVIEW"]
 
chinny_themes_df = reformatted_df.copy()
chinny_themes_df["Tag"] = reformatted_df["Tag"].apply(lambda x: determine_theme_group(x, chinny_themes))



chinny_themes_df = chinny_themes_df.drop_duplicates().groupby("Tag")["points"].agg(
         {
             "points": ["mean", "min", "max", "median", "std"],
              "Tag": ["count"]
         }         
         )
chinny_themes_df.to_csv("Point Distribution for Chinny Themes.csv")


#--------------------------------------------------------------------------------------


#Distribution of tags by question
question_df = pd.melt(reformatted_df, id_vars=["StudentID","points", "Tag"], value_vars=["q1","q2"], var_name="QuestionNumber", value_name="Question") \
.drop(columns=["QuestionNumber"]).drop_duplicates().sort_values('StudentID').reset_index(drop=True)


pd.crosstab(question_df.Question, question_df.Tag, margins = True).reset_index().to_csv("Tag Occurrence Count By Question.csv", index = False)


pd.crosstab(question_df.Question, question_df.Tag, margins = True, normalize = "index").reset_index().to_csv("Tag Occurrence Proportion By Question.csv", index = False)



#--------------------------------------------------------------------------------------

#Distribution of several tags by question
unfair_df = reformatted_df.copy()
unfair_tags = ["DOBETTER", "DQUF", "EXAMDIFFHW", "HARD", "MISLEADING", "TRICK->UNFAIR", "EXAMUNCLEAR", "UNFAIR", "UNLUCKY", "VARTOOBIG"]
unfair_df["Tag"] = reformatted_df["Tag"].apply(lambda x: categorize_unfair(x, unfair_tags))
unfair_df = pd.melt(unfair_df, id_vars=["StudentID","points", "Tag"], value_vars=["q1","q2"], var_name="QuestionNumber", value_name="Question") \
.drop(columns=["QuestionNumber"]).drop_duplicates().sort_values('StudentID').reset_index(drop=True)

pd.crosstab(unfair_df.Question, unfair_df.Tag, margins = True).reset_index().to_csv("Tag Occurrence Count By Unfair vs Other Tags.csv", index = False)

#--------------------------------------------------------------------------------------


#Distribution of tags by feedback category

feedback_df = pd.melt(df, id_vars=["StudentID", "points", "q1", "q2"], value_vars=["PreExamTags", "VarianceTags", "SecurityTags"], var_name="FeedbackCategory", value_name="Tag") \
.drop_duplicates().sort_values('StudentID').reset_index()

pd.crosstab(feedback_df.FeedbackCategory, feedback_df.Tag, margins = True).to_csv("Tag Occurrence By Feedback Category.csv")

pd.crosstab(feedback_df.FeedbackCategory, feedback_df.Tag, margins = True, normalize="index").to_csv("Tag Proportion By Feedback Category.csv")


#--------------------------------------------------

#TODO: plot. 
#Average points by tag, according to fairness.
tag_list = ["EF", "PEMF", "FAIR GAME", "CENTRAL LIMIT", "DOBETTER", "UNLUCKY", "DQUF", "VARTOOBIG"]


#---------------------------------------------------

 

