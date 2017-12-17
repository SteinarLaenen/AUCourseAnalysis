import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *

def stringcourselist():
	stringcourse_list = []
	for i in Course.objects.all():
		stringcourse_list.append(i.name)

	return stringcourse_list

courselist = stringcourselist()


question_posts = set()
counter = 0

for i in Post.objects.all():
	for j in courselist:
		if j in i.text and "thoughts" in i.text:

			question_posts.update([i.fb_id])
		if j.lower() in i.text and "thoughts" in i.text:
			question_posts.update([i.fb_id])

	if "Thoughts on" in i.text or "thoughts on" in i.text:
		question_posts.update([i.fb_id])

	if "workload" in i.text or "Workload" in i.text:
		question_posts.update([i.fb_id])


for i in question_posts:
	for j in Post.objects.filter(fb_id = i):
		print j.text + "\n"

print "Number of posts:", len(question_posts)


