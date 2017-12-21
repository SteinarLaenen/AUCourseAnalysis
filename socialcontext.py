'''General idea of how to use social context in order to rate reviews

Problem: Every post (course) has a set of reviews (comments) which will be used for a final course rating. In order to effectively rate the courses, there must be a quality measure for the comments. By looking at likes per comment we can measure quality. 

Steps:

1. Look at the likes of a review
if number_of_likes = 0:
	assign standard quality
if number_of_likes > 0:
	For every person that liked the review:
		look at total number of reviews written by person (questionable if this is a good measure)
		look at total number of likes on reviews by person
		Assign 'importance' to like of this person
	final_quality = sum of all like_importances

Based on the 'importance' of all the likes, assign a quality to the review

2. Quality of the reviewer
Data that could be used: 
	- Total number of likes the reviewer had before the review in question
	- Total number of reviews written by reviewer
	- Quality of previous reviews (where do you start)


pseudocode: 
'''
def socialcont(comment):
	'''takes comment and rates it based on social context i.e. likes by other people'''
	
	totquality = float(0)
	## like importance
	# only if the comment has likes we continue this part
	if len(comment.likes.all())>0:
		#go through all people who liked the review - 'likers'
		for user in comment.likes.all():
			likes_per_review = user.likes_per_review
			totquality += likes_per_review #NORMALIZATION NEEEDED
	
	## author_quality
	totlikesaut = comment.author.likes_per_review
	## Update total quality
	totquality += tot_likes_aut
	# total number of reviews author
	num_of_reviews_aut = len([rev for rev in Comment.objects.filter(author=user)])
	## disciplines authors
	courses = comment.courses.all() # WRONG
	disciplines = [c.discipline.all() for c in courses]
	authority = (sum([comment.author.numberofreviews_set.get(discipline==d) for d in discipline])/len(discipline))/num_of_reviews_aut ##WRONG 

	return totquality
