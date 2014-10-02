Location_Choices = []
limit = {}
main_page_markers_string = ""

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

def set_main_page_markers_string(a):
	global main_page_markers_string
	main_page_markers_string = a

def get_main_page_markers_string():
	return main_page_markers_string