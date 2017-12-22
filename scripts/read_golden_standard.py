import django
from django.conf import settings

from reviews.models import *
import json

def run(*args):
    with open('comment_id_polarity_gs_dic.txt', 'r') as f:
        comment_id_polarity_gs_dic = json.load(f)
    n = 0
    for comm_id in comment_id_polarity_gs_dic.keys():
        comment = Comment.objects.get(fb_id=int(comm_id))
        comment.polarity_gs = int(comment_id_polarity_gs_dic[comm_id])
        comment.save()
        n += 1
    print "Set golden standard of", n, "courses."
