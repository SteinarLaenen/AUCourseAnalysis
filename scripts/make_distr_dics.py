# Script that writes to text file in json format a dictionary with
# values of mean and std of a number of distributions, used to compute
# z-score by class-methods in models.py

# $ python manage.py runscript make_distr_dics
import django
from django.conf import settings
from reviews.models import *
import numpy as np

def run(*args):
    outputfilename = args[0]
    mean, std = dict(), dict()

    # Likes per review
    lpr = [u.likes_per_review for u in User.objects.filter(reviewer=True)]
    mean['LPR'] = np.mean(lpr)
    std['LPR'] = np.std(lpr)

    # Comment quality
    cq = [c.return_quality() for c in Comment.objects.all()]
    mean['CQ'] = np.mean(cq)
    std['CQ'] = np.std(cq)

    # Course authorities
    ca = []
    for reviewer in User.objects.filter(reviewer=True):
        for comment in reviewer.comments_authored.filter(review=True):
            for course in comment.courses.all():
                # Add authority of this reviewer over this course 
                ca.append(reviewer.return_course_authority(course))
                
    mean['CA'] = np.mean(ca)
    std['CA'] = np.std(ca)

    # Write dicionaries in [mean, std], through json.dumps in file
    with open(outputfilename, 'w') as f:
        f.write(json.dumps([mean, std]))

                # c_auth = 0 # Course authority of cur
                # # user over this course
                # for disc in course.discipline.all():
                #     # Add number of reviews this author wrote in this discipline
                #     c_auth += reviewer.numberofreviews_set.get(discipline=
                #                                                disc).number
                # ca.append(c_auth)

