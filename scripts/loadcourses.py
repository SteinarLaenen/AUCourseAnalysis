# Script that loads course, discipline, track, and theme instances from file
# with json. Run by
# $ python manage.py runscript loadcourses --script-args coursesjson.txt


import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from reviews.models import *
import json


NEWCOURSES = 0
EXISTCOURSES = 0
def return_instances(Model, alogiven_names):
    """Returns 'model' instances matching the names, if not existing already
    makes it first"""
    out_instances = []
    for given_name in alogiven_names: # Iter over discipline names in alogiven_names
        try:
            out_instances.append(Model.objects.get(name=given_name))
        except ObjectDoesNotExist:
            out = Model()
            out.name = given_name
            out.save()
            out_instances.append(out)
    return out_instances

def save_course(cdic):
    """Checks if course is already existing and if not, makes it"""
    global NEWCOURSES, EXISTCOURSES
    try:
        Course.objects.get(name=cdic['name']) # If does not fail, it exists
        EXISTCOURSES += 1
    except ObjectDoesNotExist: # Make instance if nonexisting yet
        out = Course()
        out.name = cdic['name']
        out.level = cdic['level']
        out.current = cdic['current']
        out.save() # Save before adding m2m relations
        # Iterate over discipline, theme, and track instances
        for d in return_instances(Discipline, cdic['discipline']):
            out.discipline.add(d)
        for d in return_instances(Theme, cdic['theme']):
            out.theme.add(d)
        for d in return_instances(Track, cdic['track']):
            out.track.add(d)
        out.save()
        NEWCOURSES += 1


def run(*args):
    file_loc = args[0]
    with open(file_loc, 'r') as f:
        list_of_course_dics = json.load(f) # list with dics for each course
        # with following keys: name, level, discipline, theme, track, current
        for course_dic in list_of_course_dics:
            save_course(course_dic)
    print ''.join(["Added ", str(NEWCOURSES), " new courses to db.\n",
                   str(EXISTCOURSES), " were already known."])
