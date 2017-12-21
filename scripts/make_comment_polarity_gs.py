# Run by
# $ python manage.py runscript make_comment_polarity_gs --script-args <number of
# comments you want to rate>
# Saves input values to respective comment's 'polarity_gs' attribute
# Each print of the comment's text is accompanied by the comment's database id
# So in case mistakes are made, one can go back manually
import django
from django.conf import settings

from reviews.models import *
from random import shuffle

def run(*args):
    target = int(args[0])
    review_comments = list(Comment.objects.filter(
        review=True).filter(polarity_gs=-2))
    shuffle(review_comments)
    pol_dic = {-1: 0, 0: 0, 1: 0, 3:0}
    for i, comment in enumerate(review_comments):
        if i == target:
            break
        print  ''.join(['(',unicode(comment.id),')']), '------------------------------------------\n'
        print comment.text, '\n'
        pol_gs = int(input("POLARITY OF ABOVE COMMENT IS: "))

        if pol_gs == 3:
            comment.review= False
            comment.polarity_gs = pol_gs # Set to 3 to later see which comments
            # manually removed
            print "Set 'review' attribute of this comment as 'False'."
        elif -1  <= pol_gs <= 1:
            comment.polarity_gs = pol_gs
            print ' '.join(["Updated polarity of comment",
                            ''.join(['(',unicode(comment.id),')']),
                            "as", unicode(pol_gs)])
        pol_dic[pol_gs] += 1            
        comment.save()

    print "Updated polarity_gs attribute of", target, "comments."
    print pol_dic[1], "POSITIVES,", pol_dic[0], "NEUTRALS,", pol_dic[-1], "NEGATIVES"
    print pol_dic[3], 'comments were identified as irrelevant.'

                        
