# Script that writes to text file in json format a dictionary with
# values of min and max of a number of values, used for feature scaling
# by class-methods in models.py

# $ python manage.py runscript make_min_max_dics
import django
from django.conf import settings
from reviews.models import *


def run(*args):
    outputfilename = args[0]
    min_v, max_v = dict(), dict()

    # Likes per review
    lpr = [u.likes_per_review for u in User.objects.filter(reviewer=True)]
    min_v['LPR'] = min(lpr)
    max_v['LPR'] = max(lpr)

    # Comment quality
    cq = [c.return_quality() for c in Comment.objects.all()]
    min_v['CQ'] = min(cq)
    max_v['CQ'] = max(cq)

    # Course authorities
    ca = []
    for reviewer in User.objects.filter(reviewer=True):
        for comment in reviewer.comments_authored.filter(review=True):
            for course in comment.courses.all():
                # Add authority of this reviewer over this course 
                ca.append(reviewer.return_course_authority(course))
                
    min_v['CA'] = min(ca)
    max_v['CA'] = max(ca)

    # Write dicionaries in [mean, std], through json.dumps in file
    with open(outputfilename, 'w') as f:
        f.write(json.dumps([min_v, max_v]))

                # c_auth = 0 # Course authority of cur
                # # user over this course
                # for disc in course.discipline.all():
                #     # Add number of reviews this author wrote in this discipline
                #     c_auth += reviewer.numberofreviews_set.get(discipline=
                #                                                disc).number
                # ca.append(c_auth)

