# Sets status of 'reviewer' accordingly to authors of comments that are reviews
# and subsequently updates the 'likes_per_reviewer' and number_of_reviews_in
# relation
# python manage.py runscript update_reviewer_stats

import django
from django.conf import settings

from reviews.models import *


def run(*args):
    nofauthors = 0 
    for c in Comment.objects.filter(review=True):
        c.author.reviewer = True
        c.author.save()

    for author in User.objects.filter(reviewer=True):
        nofauthors += 1
        author.update_reviews_written()
        author.update_likes_per_review()    
        author.save()
    print "Updated stats for", nofauthors, "users"
