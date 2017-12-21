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
	# only if the cmment has likes we continue
	if len(comment.likes.all())>0:
		#go through all people who liked the review - 'likers'
		for user in comment.likes.all():
			# go through all reviews written by liker
			reviewsbyuser = [com for com in Comment.objects.filter(author=user) if com.review] 
			num_of_reviews = float(len(reviewsbyuser))
			# get total likes on all reviews written by liker
			totlikes = float(0)
			for comment2 in reviewsbyuser:
				totlikes += float(len(comment2.likes.all()))
			if num_of_reviews == float(0):
				continue
			else: 
				# total quality/importance of like is like per review by liker
				totquality += float(totlikes / num_of_reviews) #(NORMALIZATION NEEDED)
	
	#number of likes on review itself, can be disregarded if author_quality is implemented
	totquality += float(len(comment.likes.all()))
	
	## author_quality
	# look at other reviews written by this reviewer
	reviewsbyauthor = [rev for rev in Comment.objects.filter(author=comment.author) if rev.review]
	num_of_reviews_aut = float(len(reviewsbyauthor))
	totlikesaut = float(0)
	#total number of likes of this reviewer
	for comment3 in reviewsbyauthor:
		totlikesaut += float(len(comment3.likes.all()))
	if num_of_reviews_aut == float(0):
		pass
	else: 
		totquality += float(totlikesaut / num_of_reviews_aut)
	return totquality

def socialcont2(comment):
