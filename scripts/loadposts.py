# Loads posts and users from Excellent and Diverse people of AUC group
# $ python manage.py runscript loadposts --script-args <ACCESS_TOKEN>

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *
from collections import Counter
import requests
import facebook

# AUX FUNCS
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
def save_post(json_dic, author_id):
    """Given json_dic with post info, and author_id, checks if post already 
    exists and if not makes it and saves it"""
    try:
        Post.objects.get(fb_id=json_dic['id'])
    except ObjectDoesNotExist:
        p = Post()
        p.make(json_dic, author_id)
        p.save()


def run(*args):
    token = args[0]
    graph = facebook.GraphAPI(access_token=token)
    group_results = graph.search(type='group',
                                 q='The excellent and diverse people of AUC')
    target_group_id = group_results['data'][0]['id']
    fbid_userid_dic = Counter(dict((u.fb_id, u.id) for u in User.objects.all())) # Stores fb_id: user_id where user_id is unique
    # db id
    users_added = 0
    for user_dic in graph.get_all_connections(id=target_group_id,
                                          connection_name='members',
                                          fields='id,name'):
        fbid_userid_dic[user_dic['id']] = return_user_id(user_dic)
        users_added += 1
    print "Added ", users_added, " users."
    posts_added = 0
    post_fields = 'from,id,created_time,message'
    for post_dic in graph.get_all_connections(id=target_group_id,
                                              connection_name="feed",
                                              fields=post_fields):
        if any(not post_dic.has_key(field) for field in
               ['from', 'id', 'created_time', 'message']):
            continue # If any field is not present, do not continue
        author_fb_id = post_dic['from']['id']
        author_id = fbid_userid_dic[author_fb_id] 
        if author_id == 0: # If author_fb_id not in dictionary
            author_id = return_user_id(post_dic['from'])
            fbid_userid_dic[author_fb_id] = author_id
        save_post(post_dic, author_id)
        posts_added += 1
        if (posts_added % 500) == 0:
            print posts_added, " posts added."
