# Identifies courses in all the comments in the db that are replies to requests
# $ python manage.py runscript identify_courses_in_comments

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from review.models import *


STOPWORDS = nltk.corpus.stopwords.words('english') # TO BE DEFINED


def tokenize(post):
    global STOPWORDS
    wordlist = nltk.tokenize.word_tokenize(post)
    wordlist = [word.lower() for word in wordlist]
    filteredlist = [word for word in wordlist if
                    word not in STOPWORDS and (word.isalnum()
                                               or any(word == sign for sign
                                                      in ('?' or '-' or '*')))]
    stemmedlist = [nltk.LancasterStemmer().stem(word) for word in filteredlist]
    return stemmedlist


# Map course name to course db id
coursename_id_dic = dict((unicode(c.name.lower()), c.id) for
                         c in Course.objects.all())

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

# Manually defined alternative words for introduction
manualabbrev_dic = {
    'introduction': {'intro'},
    'advanced': {'adv'},
    'psychology':{ 'psych'}}
                    
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
for coursename in coursenames:
    course_cond = []
    for rel_courseword in coursename_relwords_dic[coursename]:
        course_cond.append(courseword_abbrevs[rel_courseword])
    coursename_course_cond_dic[coursename] = course_cond
# AUX FUNCS
def return_courses(text, aloc):
    """Given a text and potential courses, returns courses that it 
    identified in the post"""
    global coursename_id_dic, coursenames, coursename_relwords_dic
    global courseword_frequency, courseword_abbrevs, abbrevs
    textlower = text.lower() # posttext # post.text.lower()
    processed_text = tokenize(textlower) # BEREND(post.text)
    out = set()
    plausible_courses = aloc
    for coursename in plausible_courses:
        # THIS CONDITION SHOULD BE INCLUDED IN COMMENTS ONLY USING ALREADY RELEVANT
        # COURSES, OTHERWISE GOING TO BE TO HARD
        # FIrst check if any of associated course words is
        # unique (i.e. satisfies presence of this course
        # (e.g. gastronomy occurs only once in all courses, hence no need for
        # full name)        
        for course_word in coursename_relwords_dic[coursename]:
            if (courseword_frequency[course_word] == 1 and
            any(abbrev in processed_text for abbrev in
                courseword_abbrevs[course_word])):
                out.add(coursename)
                continue
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
    i, j = 0, 0
    for post in Post.objects.filter(request=True):
        comments = post.comment_set.all()
        post_coursenames = [c.name.lower() for c in post.courses.all()]
        for comment in comments:
            textlower = comment.text.lower()
            courses_identified = return_courses(textlower, post_coursenames)
            if courses_identified == set():
                continue # No courses identified so skip
            # Else, add identified courses and set comment 'review' attribute to
            # True
            for course_id in courses_identified:
                j += 1
                comment.courses.add(course_id)
            comment.review=True
            i += 1
            comment.save()
    print "Identified", i, "comments that link, in total,", j "many times to courses"
