import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import csv
from reviews.models import *
import re
import json

import nltk
import sklearn
import numpy as np
import matplotlib.pyplot as plt

from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn