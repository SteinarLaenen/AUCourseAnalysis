import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *



counter = 0

for i in Post.objects.all():
	if "thoughts" and "workload" in i.text:
		print i.text
		counter += 1

print "Number of posts:", counter
