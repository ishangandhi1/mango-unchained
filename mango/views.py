from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from mango.models import Category, Page

def encdec(categ,scheme):
	if scheme == 'encode':
		return categ.replace(' ',' ')

	else:
		return categ.replace('_',' ')


def index(request):
	#return HttpResponse("Mango says hello world! <a href='/mango/about'>About</a>")
	context = RequestContext(request)
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories': category_list,'pages': page_list}
	for category in category_list:
		category.url = encdec(category.name,'encode')
	return render_to_response('mango/index.html',context_dict,context)

def about(request):
	return HttpResponse("Mango says: This is the about page <a href='/mango/'>Index</a>")


def category(request,category_name_url):
	context = RequestContext(request)
	category_name = encdec(category_name_url,'decode')
	context_dict = {'category_name': category_name}
	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
	except Category.DoesNotExist:
		pass

	return render_to_response('mango/category.html',context_dict,context)





