import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *
import re
import json

def stringcourselist():
	stringcourse_list = []
	for i in Course.objects.all():
		stringcourse_list.append(i.name)

	return stringcourse_list

courselist = stringcourselist()


question_posts = set()
counter = 0

def run():
    for i in Post.objects.all():
            # Check if coursename + word thoughts is in text, add that post
            for j in courselist:
                    if j in i.text and "thoughts" in i.text:
                    #if re.search(j, i.text):
                            question_posts.update([i.fb_id])
                            i.request = True
                            i.save()
                    if j.lower() in i.text and "thoughts" in i.text:
                            question_posts.update([i.fb_id])
                            i.request = True
                            i.save()
            #Adds some non-relevant posts
            # most posts start with thoughts on
            #if "Thoughts on" in i.text or "thoughts on" in i.text:
            #	question_posts.update([i.fb_id])

            # If post contains word workload add it
            #if "workload" in i.text or "Workload" in i.text:
            #	question_posts.update([i.fb_id])

    # Check if post asks about course
    for i in question_posts:
            for j in Post.objects.filter(fb_id = i):
                    print i + "\n" + j.text + "\n"

    print "Number of posts:", len(question_posts)




    with open("filtered_posts_fbid.txt", "wb") as outfile:
            outfile.write(json.dumps(list(question_posts)))

            
