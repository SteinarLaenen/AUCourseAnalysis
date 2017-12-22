# BEREND's prepping text::
# General idea of how to use social context in order to rate reviews

# Problem: Every post (course) has a set of reviews (comments) which will be used for a final course rating. In order to effectively rate the courses, there must be a quality measure for the comments. By looking at likes per comment we can measure quality. 

# Steps:

# 1. Look at the likes of a review
# if number_of_likes = 0:
# 	assign standard quality
# if number_of_likes > 0:
# 	For every person that liked the review:
# 		look at total number of reviews written by person (questionable if this is a good measure)
# 		look at total number of likes on reviews by person
# 		Assign 'importance' to like of this person
# 	final_quality = sum of all like_importances

# Based on the 'importance' of all the likes, assign a quality to the review

# 2. Quality of the reviewer
# Data that could be used: 
# 	- Total number of likes the reviewer had before the review in question
# 	- Total number of reviews written by reviewer
# 	- Quality of previous reviews (where do you start)
import django
from django.conf import settings

from reviews.models import *


def socialcont(comment):
	"""takes comment and rates it based on social context i.e. likes by 
        other people"""
        author = comment.author
	comm_qual = comment.return_quality()

        author_qual = comment.author.likes_per_review

        author_disciplines = author.numberofreviews_set.all()

        # List with authorities of author for each course discussed in comment
        author_course_authorities = []
        for course in comment.courses.all():
                author_course_authorities.append(
                        author.return_course_authority_scaled(course))
        if len(comment.courses.all()) == 0:
                overall_author_authority = 0
        else:
                overall_author_authority = (sum(author_course_authorities)/
                                            len(author_course_authorities))

	return comm_qual+ author_qual +overall_author_authority

def run(*args):
        for c in Comment.objects.filter(review=True):
                qual = socialcont(c)
                c.quality_measure = qual
                c.save()
