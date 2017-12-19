# Loads posts and users from Excellent and Diverse people of AUC group
# $ python manage.py runscript loadposts --script-args <ACCESS_TOKEN> <file
# with set of fb_ids of relevant posts>

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *
from collections import Counter
import requests
import facebook
import json

def unroll_items(data_paging_dic, *args):#, start_cond, end_cond)
    """Takes a dic with paging and data keys, returns generator object that 
    allows easy iteration over the actual data elements. Start returning only
    when start_cond has been matched, and stops iterating when end_cond has been
    satisfied, start and end_cond are functions"""
    started = False
    ended = False
    try:
        start_func = args[0]
        end_func = args[1]
    except IndexError: # If no function provided
        start_func = lambda x: True 
        end_func = lambda x: False
    continue_mining = True
    while continue_mining:
        for el in data_paging_dic['data']:
            if end_func(el):
                continue_mining = False
                break
                # If matches end func, stop
            elif start_func(el): # If matches start_func, yield
                yield el
        if data_paging_dic['paging'].has_key('next'):
            req = requests.get(data_paging_dic['paging']['next'])
            data_paging_dic = req.json() # Get new results again
        else: # If no next anymore, we have iterated over all items
            break


def run(*args):
    token = args[0]
    with open(args[1], 'rb') as f:
        post_fbids = json.load(f)
    graph = facebook.GraphAPI(access_token=token)
    comment_fields = 'created_time,likes,id,from,message'
    fbid_userid_dic = Counter(dict((u.fb_id, u.id) for u in User.objects.all()))
    comments_added = 0
    for post_fbid in post_fbids:
        try:
            post_instance = Post.objects.get(fb_id=post_fbid)
        except ObjectDoesNotExist:
            print "Post object with fb id", post_fbid, "was not found"
        # extract comments, only on  posts, skip comments on comments for now
        for comment_dic in graph.get_all_connections(id=post_fbid,
                                                     connection_name="comments",
                                                     fields=comment_fields):
            new_c = Comment()
            new_c.make(comment_dic)
            new_c.post = post_instance
            author_id = fbid_userid_dic[comment_dic['from']['id']] # get
            # db id for user
            if author_id == 0:
                print ("User (author) with name", comment_dic['from']['name'],
                       "was not found")
            else:
                new_c.author_id = author_id
            new_c.save()
            # add likes
            if comment_dic.has_key('likes'):
                for user_dic in unroll_items(comment_dic['likes']):
                    userid = fbid_userid_dic[user_dic['id']]
                    if userid == 0:
                        print ("User (liker) with name", user_dic['name'],
                               "was not found")
                    else:
                        new_c.likes.add(userid)

                # try:
                #     new_c.likes.add(User.objects.get(fb_id=user_dic['id']))
                # except ObjectDoesNotExist:
                    
            new_c.save()
            comments_added += 1
            if comments_added% 100 == 0:
                print "Loaded", comments_added, "comments"

                
    # for user_dic in graph.get_all_connections(id=target_group_id,
    #                                       connection_name='members',
    #                                       fields='id,name'):
    #     fbid_userid_dic[user_dic['id']] = return_user_id(user_dic)
    #     users_added += 1
    # print "Added ", users_added, " users."
    # posts_added = 0
    # post_fields = 'from,id,created_time,message'
    # for post_dic in graph.get_all_connections(id=target_group_id,
    #                                           connection_name="feed",
    #                                           fields=post_fields):
    #     if any(not post_dic.has_key(field) for field in
    #            ['from', 'id', 'created_time', 'message']):
    #         continue # If any field is not present, do not continue
    #     author_fb_id = post_dic['from']['id']
    #     author_id = fbid_userid_dic[author_fb_id] 
    #     if author_id == 0: # If author_fb_id not in dictionary
    #         author_id = return_user_id(post_dic['from'])
    #         fbid_userid_dic[author_fb_id] = author_id
    #     save_post(post_dic, author_id)
    #     posts_added += 1
# AUX FUNCS
