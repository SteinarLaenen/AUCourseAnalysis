import django
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist

import requests
from django.conf import settings

class Course(models.Model):
    """Represents a particular course at AUC"""
    name = models.CharField(max_length=50, null=True)
    discipline = models.ManyToManyField('Discipline', related_name='Discipline')
    theme = models.ManyToManyField('Theme')
    track = models.ManyToManyField('Track')
    level = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name



class Discipline(models.Model):
    name = models.CharField(max_length=3)
    
    def __str__(self):
        return self.name

class Track(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Theme(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
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
    author = models.ForeignKey('User')
    request = models.BooleanField(default=False)
    courses = models.ManyToManyField(Course) # If request, this
    # links to the courses that are asked fb for in the post
    
class User(models.Model):
    """Represents a user on facebook"""
    reviewer = models.BooleanField(default=False) # If user has reviewed at
    # least once
    fb_id = models.CharField(max_length=100)
    name = models.CharField(max_length=25)
    trust = models.ManyToManyField('self', through='TrustRelation',
                                    symmetrical=False) # represents
    # trust towards other users, 'through TrustRelation' allows to store
    # extra data with this 'edge' (see TrustRelation)

    # trusted_by = models.ManyToManyField('self', through='TrustRelation',
    #                                 symmetrical=False)    
    def __str__(self):
        names = self.name.split()
        if self.reviewer:
            return ' '.join([fname[0] for fname in names[:-1]]+[names[-1]]+
                            '(rev)')
        else:
            return ' '.join([fname[0] for fname in names[:-1]]+[names[-1]])

class Comment(models.Model):
    """Represents a single comment, if self.review then it represents a review
    else it is just a regular comment"""
    fb_id = models.CharField(max_length=100)
    likes = models.ManyToManyField(User, related_name='liked')
    date_posted = models.CharField(max_length=10)
    author = models.ForeignKey(User, related_name='reviews')
    text = models.CharField(max_length=5000, default='')

    post = models.ForeignKey(Post)
    review = models.BooleanField(default=False)
    course = models.ForeignKey(Course)
    polarity = models.FloatField(default=0)

    def __str__(self):
        return self.text[:10]
    


# class Request(models.Model):
#     """Represents a facebook post in which a user requests opinions/thoughts on
#     one or more courses"""
#     author = models.ForeignKey(User)
#     courses = models.ManyToManyField(Course)
#     comments = models.ManyToManyField(Post)
