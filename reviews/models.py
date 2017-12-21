import django
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import requests
from django.conf import settings
from django.db import DatabaseError 

class Course(models.Model):
    """Represents a particular course at AUC"""
    name = models.CharField(max_length=50, null=True)
    discipline = models.ManyToManyField('Discipline', related_name='Discipline')
    theme = models.ManyToManyField('Theme')
    track = models.ManyToManyField('Track')
    level = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.name

class Discipline(models.Model):
    name = models.CharField(max_length=3, unique=True)
    
    def __unicode__(self):
        return self.name

class Track(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.name

class Theme(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

class TrustRelation(models.Model):
    """Model that functions as an intermediary between Reviewers,
    stores extra data such as strenght of trust and 
    areas in which trust has been given"""
    recipient = models.ForeignKey('User', related_name='trusted_by')
    sender = models.ForeignKey('User', related_name='trusts')
    strength = models.FloatField()
    
class Post(models.Model):
    """Represents a post in a facebook group"""
    fb_id = models.CharField(max_length=100, default='', unique=True)
    author = models.ForeignKey('User', related_name='posts_authored')
    text = models.CharField(max_length = 5000, default='')
    date_posted = models.CharField(max_length=10, default='')
    time_posted = models.CharField(max_length=10, default='')
    request = models.BooleanField(default=False)
    courses = models.ManyToManyField(Course) # If request, this
    # links to the courses that are asked fb for in the post
    likes = models.ManyToManyField('User', related_name='posts_liked')
    
    def __unicode__(self):
        try:
            return ' '.join([unicode(self.author), self.date_posted[:4],
                             unicode(self.id)])
        except ObjectDoesNotExist:
            return ' '.join(['Unknown author', self.date_posted[:4],
                             unicode(self.id)])
    def make(self, json_dic, author_id):
        """Given a json dic and the db id of the author of the posts, makes post 
        instance"""
        self.author = User.objects.get(id=author_id)
        self.fb_id = json_dic['id']
        self.date_posted = json_dic['created_time'][:10]
        self.time_posted = json_dic['created_time'][11:16]
        try:
            self.text = json_dic['message']
        except DatabaseError:# In case message is too long
            self.text = 'DATABASEERORR: Message too long'
    def show_comments(self):
        print 'Post:', unicode(self.author), self.date_posted, self.time_posted, ':\n',
        print self.text,'\n---------------------------------------------------------'
        for comment in self.comment_set.order_by('date_posted','time_posted'):
            try:
                print ''.join([unicode(comment.author),'(',
                               comment.date_posted,comment.time_posted,':',
                               comment.text])
            except ObjectDoesNotExist:
                print ''.join(['Unknown author','(',
                               comment.date_posted,comment.time_posted,':',
                               comment.text])
            print '---------------------------------------------------------'
    
class User(models.Model):
    """Represents a user on facebook"""
    reviewer = models.BooleanField(default=False) # If user has reviewed at
    # least once
    fb_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=25)
    trust = models.ManyToManyField('self', through='TrustRelation',
                                    symmetrical=False) # represents
    # trust towards other users, 'through TrustRelation' allows to store
    # extra data with this 'edge' (see TrustRelation)

    # trusted_by = models.ManyToManyField('self', through='TrustRelation',
    #                                 symmetrical=False)    
    def __unicode__(self):
        # names = self.name.encode('utf-8').split()
        if self.reviewer:
            return self.name + ' (rev)'
        else:
            return self.name

    def make(self, json_dic):
        """Given dic with info as encountered in fb API, updates values
        accordingly"""
        self.name = json_dic['name']
        self.fb_id = json_dic['id']
        
        

class Comment(models.Model):
    """Represents a single comment, if self.review then it represents a review
    else it is just a regular comment"""
    fb_id = models.CharField(max_length=100, default='', unique=True)
    likes = models.ManyToManyField(User, related_name='comments_liked')
    date_posted = models.CharField(max_length=10) # YYYY:MM:DD
    time_posted = models.CharField(max_length=4, default='') # HH:MM
    author = models.ForeignKey(User, related_name='comments_authored')
    text = models.CharField(max_length=5000, default='')

    post = models.ForeignKey(Post)
    review = models.BooleanField(default=False)
    courses = models.ManyToManyField(Course)
    # Golden standard, set to -2 to know that is has not been rated
    polarity_gs = models.FloatField(default=-2)
    # Polarity as predicted 
    polarity_predicted = models.FloatField(default=-2)

    def __unicode__(self):
        try:
            return ' '.join([unicode(self.author), unicode(self.post.id)])
        except ObjectDoesNotExist:
            return ' '.join([u'Unknown author', unicode(self.post.id)])
    
    def make(self, json_dic):
        """Given a fb dic, makes instance of comment accordingly, does not set 
        post relationship because post instance is loaded once in script
        already, same for likes because we need a connection to facebook to get 
        all users that liked it"""
        self.date_posted = json_dic['created_time'][:10]
        self.time_posted = json_dic['created_time'][11:16]
        self.fb_id = json_dic['id']
        self.text = json_dic['message']

        try:
            self.author = User.objects.get(fb_id=json_dic['from']['id'])
        except ObjectDoesNotExist:
            print "Author with name", json_dic['from']['name'], 'was not found'


        
# class Request(models.Model):
#     """Represents a facebook post in which a user requests opinions/thoughts on
#     one or more courses"""
#     author = models.ForeignKey(User)
#     courses = models.ManyToManyField(Course)
#     comments = models.ManyToManyField(Post)
