global Location_Choices
Location_Choices = []
global limit
limit = {}

def get_Location_Choices():
	return Location_Choices

def get_limit():
	return limit

def set_Location_Choices(a):
	global Location_Choices
	Location_Choices = a

def set_limit(a):
	global limit
	limit = a