# Identifies posts that request course reviews and identifies the courses
# mentioned, updates database accordingly
# $ python manage.py runscript identify_courses_in_posts --script-

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *
from collections import Counter
import requests
import facebook
import re
import nltk

STOPWORDS = nltk.corpus.stopwords.words('english') # TO BE DEFINED


def posttokens(post):
    global STOPWORDS
    wordlist = nltk.tokenize.word_tokenize(post)
    wordlist = [word.lower() for word in wordlist]
    filteredlist = [word for word in wordlist if
                    word not in STOPWORDS and (word.isalnum()
                                               or any(word == sign for sign
                                                      in ('?' or '-' or '*')))]
    stemmedlist = [nltk.LancasterStemmer().stem(word) for word in filteredlist]
    return stemmedlist

BEREND = posttokens # Function that converts text to tokenized/stemmed

# Map course name to course db id
coursename_id_dic = dict((unicode(c.name.lower()), c.id) for
                         c in Course.objects.all() if 'internship' not in
                         c.name.lower())

courseid_name_dic = dict((coursename_id_dic[key], key) for key in
                         coursename_id_dic.keys())

coursenames = set(coursename_id_dic.keys()) # Set of course names

# Map  course name to list with words in coursename minus stopwords
coursename_relwords_dic = dict()


# Map abbreviations/alternative versions to list with courses to which they belong
abbrev_courses_dic = dict()
# Initialize stemmers
lancstemmer = nltk.LancasterStemmer()
porterstemmer = nltk.PorterStemmer()

courseword_abbrevs = Counter()

# Mistakes of algorithm found, manually defined in dic below
# coursename_manualabbrev_dic = {
#     "basic research methods and statistics": "brms",
#     "performing arts - theatre": "performing arts",
#     "brain and mind (for ssc students)": "brain and mind",
#     "calculus for economics": "calculus for econ",
#     "human rightstand security": "human rights & security",
#     "performing arts - music": "performing arts",
#     "classical and modern sociological thought":
#     "classical & modern sociological thought",
#     "international political economy (ipe)": "international political economy",
#     "advanced logic": "advanced logic",
#     "market failure, institutions and economic policy": "market failure",
#     "existentialism in literature and philosophy":
#     "existentialismtin lit and philo",
#     "human body i": "human body i"}

# Manually defined alternative words for introduction
manualabbrev_dic = {
    'introduction': {'intro'},
    'advanced': {'adv'},
    'psychology':{ 'psych'},
    }


# FIX PHILOSOPH 
                    
for cname in coursenames:
    rel_words = [word for word in re.findall('[0-9a-z]+', cname) if
                 word not in STOPWORDS]
    coursename_relwords_dic[cname] = rel_words
    for courseword in rel_words:
        similar_word_set = set()
        if courseword in manualabbrev_dic.keys():
            similar_word_set.update(manualabbrev_dic[courseword])        
        similar_word_set.add(courseword)
        similar_word_set.add(lancstemmer.stem(courseword))
        similar_word_set.add(porterstemmer.stem(courseword))
        courseword_abbrevs[courseword] = similar_word_set
        for abbrev in similar_word_set:# Map course word alternatives to
            # course names
            if abbrev_courses_dic.has_key(abbrev):
                abbrev_courses_dic[abbrev].add(cname)
            else:
                abbrev_courses_dic[abbrev] = {cname}
                
abbrevs = set(abbrev_courses_dic.keys())

courseword_frequency = Counter() # Map courseword to  frequency
# in other course names (e.g. 'world' occurs 6 times in course names)
for cname in coursenames:
    courseword_frequency.update(Counter(coursename_relwords_dic[cname]))

# Map course name to a list with sets of alternative course words
# E.g.: 'introduction to biology' would map to something like:
# [{'intro', 'introduction', 'introduc'}, {'biology', 'bio', 'biolog'}]
coursename_course_cond_dic = dict()


dict() # Map coursenames to manually defined
# abbreviations

for coursename in coursenames:
    course_cond = []
    for rel_courseword in coursename_relwords_dic[coursename]:
        course_cond.append(courseword_abbrevs[rel_courseword])
    coursename_course_cond_dic[coursename] = course_cond

    
        
# AUX FUNCS
def return_courses(posttext):
    """Given a post instance, returns courses that it identified in the post"""
    global coursename_id_dic, coursenames, coursename_relwords_dic
    global courseword_frequency, courseword_abbrevs, abbrevs
    textlower = posttext # post.text.lower()
    processed_text = BEREND(textlower) # BEREND(post.text)
    out = set()
    out.update(set(cname for cname in coursenames if cname in textlower))
    abbrevs_found = [a for a in abbrevs if a in processed_text]
    # Get relevant course words (filtered stopwords)
    plausible_courses = set()
    for abb in abbrevs_found:
        plausible_courses.update(abbrev_courses_dic[abb])
    for coursename in plausible_courses:
        # THIS CONDITION SHOULD BE INCLUDED IN COMMENTS ONLY USING ALREADY RELEVANT
        # COURSES, OTHERWISE GOING TO BE TO HARD
        # FIrst check if any of associated course words is
        # unique (i.e. satisfies presence of this course
        # (e.g. gastronomy occurs only once in all courses, hence no need for
        # full name)        
        # for course_word in coursename_relwords_dic[coursename]:
        #     if (courseword_frequency[course_word] == 1 and
        #     any(abbrev in processed_text for abbrev in
        #         courseword_abbrevs[course_word])):
        #         out.add(coursename)
        #         continue


        # Else check if course_cond is satisifed, i.e. any of alterantives versions
        # of course words are identified in right order
        course_cond = coursename_course_cond_dic[coursename]
        span = len(course_cond)
        for i in range(len(processed_text)-span):
            window = processed_text[i:i+span]
            if all(window[j] in course_cond[j] for j in range(span)):
                out.add(coursename)
                continue
    # Filter such that e.g. both 'philosophy' and 'philosophy in literature'
    # have been identified, it keeps only the longest match to prevent overmatching
    # Take ids of those courses by using mapping from coursename_id_dic
    out = set(coursename_id_dic[el] for el in out if
              all(el==sec_el or el not in sec_el for sec_el in out))
    return out


def run(*args):
    """Links posts to courses mentioned and checks if they are 
    asking for feedback"""
    request_tokens = {'thought', 'comment', 'workload', 'feedback'}# Words indicative
    # of asking for feedback

    # Words added by inspection, e.g. people tends to refer to ppl taking that
    # class, hence not asking for feedback
    undesired_tokens = {'teacher', 'lecturer', 'prof', 'manual',
                        'switch', 'people', 'guys', 'grade', 'offer', 'regist'} 
    # Set with ids of courses with 'book' in its name  because if
    # 'return_courses' identified courses but the word 'book' is in the post
    # text, it most likely concerns asking for books
    BOOK_IDS = {course.id for course in 
                Course.objects.filter(name__contains='book')}
    i = 0
    out = []
    # f = open('post_identification_test.txt', 'w')
    for post_inst in Post.objects.filter(text__contains='?'):

        textlower = post_inst.text.lower()
        # Check if undesired words are in there
        if any(word in textlower for word in undesired_tokens):
            continue
        
        # Preliminary condition of any request_token (see above)
        # must be satisfied
        if any(word in textlower for word in request_tokens):
            identified_courses = return_courses(textlower)
            if identified_courses == set():
                continue # No courses identified so go to next post
            
            
            # If no 'book' course is identifed, yet 'book' is in the post,
            # skip it because most likely asking for books
            if (BOOK_IDS.intersection(identified_courses) == set() and
                'book' in textlower):
                continue
            post_inst.request=True
            i += 1
            for course_id in identified_courses:
                post_inst.courses.add(course_id)
            post_inst.save()
            out.append(post_inst)
            # f.write(''.join(["Identified: ", ', '.join(identified_courses), ' in\n',post_inst.text,'\n--------------------------------------------------------\n']).encode('utf-8'))
        else:
            continue # If none of keywords in post, likely not relevant
    print "Found", i, "posts that ask for course reviews"
