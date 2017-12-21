# Loads posts and users from Excellent and Diverse people of AUC group
# $ python manage.py runscript loadposts --script-args <ACCESS_TOKEN>

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *
from collections import Counter
import requests
import facebook
import json

def return_user_id(json_dic):
    """Given a json_dic with keys as defined in network.models.User, 
    return user either from db if it already existed, otherwise makes new user"""
    try:
        return User.objects.get(fb_id=json_dic['id']).id
    except ObjectDoesNotExist:
        out = User()
        out.make(json_dic)
        out.save()
        return out.id

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
    # with open(args[1], 'rb') as f:
    #     post_fbids = json.load(f)
    graph = facebook.GraphAPI(access_token=token)
    comment_fields = 'created_time,likes,id,from,message'
    fbid_userid_dic = Counter(dict((u.fb_id, u.id) for u in User.objects.all()))
    comments_fbids = set([c.fb_id for c in Comment.objects.all()]) 
    comments_added = 0
    rel_posts = Post.objects.filter(request=True)# Get relevant posts
    for post_instance in rel_posts:
        # try:
        #     post_instance = Post.objects.get(fb_id=post_fbid)
        # except ObjectDoesNotExist:
        #     print "Post object with fb id", post_fbid, "was not found"
        #     continue
        # extract comments, only on  posts, skip comments on comments for now
        # try:
        #     post_comment_generator = 

        #     continue
        post_fbid = post_instance.fb_id
        try:
            for comment_dic in graph.get_all_connections(id=post_fbid,
                                                         connection_name="comments",
                                                         fields=comment_fields):
                if comment_dic['id'] in comments_fbids:
                    continue
                new_c = Comment()
                new_c.make(comment_dic)
                new_c.post = post_instance
                author_dic = comment_dic['from']
                author_id = fbid_userid_dic[author_dic['id']] # get
                # db id for user
                if author_id == 0:
                    author_id = return_user_id(author_dic)
                    fbid_userid_dic[author_dic['id']] = author_id
                    print ("User (author) with name", author_dic['name'],
                           "was not found, but added now")
                new_c.author_id = author_id
                new_c.save()
                # add likes
                if comment_dic.has_key('likes'):
                    for user_dic in unroll_items(comment_dic['likes']):
                        user_id = fbid_userid_dic[user_dic['id']]
                        if user_id == 0:
                            user_id = return_user_id(user_dic)
                            fbid_userid_dic[user_dic['id']] = user_id
                            print ("User (liker) with name", user_dic['name'],
                                   "was not found")
                        new_c.likes.add(user_id)
                new_c.save()
                comments_added += 1
                if comments_added% 100 == 0:
                    print "Loaded", comments_added, "comments"
        except facebook.GraphAPIError:
            print ("Post by", post_instance.author.name, post_instance.date_posted,
                   "does not exist anymore")    
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
