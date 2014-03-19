from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
	#return HttpResponse("Mango says hello world! <a href='/mango/about'>About</a>")
	context = RequestContext(request)
	context_dict = {'boldmessage': "A context to the people"}
	return render_to_response('mango/index.html',context_dict,context)

def about(request):
	return HttpResponse("Mango says: This is the about page <a href='/mango/'>Index</a>")

