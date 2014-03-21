from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from mango.models import Category, Page
from mango.forms import CategoryForm, PageForm


def encdec(categ,scheme):
	if scheme == 'encode':
		return categ.replace(' ','_')

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
		context_dict['category_name_url'] = category_name_url
	except Category.DoesNotExist:
		raise Http404

	return render_to_response('mango/category.html',context_dict,context)


def add_category(request):
	context = RequestContext(request)
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()

	return render_to_response('mango/add_category.html', {'form':form},context)

def add_page(request, category_name_url):
	context = RequestContext(request)
	category_name = encdec(category_name_url,'decode')
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			page = form.save(commit=False)
			try:
				cat = Category.objects.get(category_name)
				page.category = cat
			except Category.DoesNotExist:
				return render_to_response('/mango/add_category.html',{},context)

			page.views = 0
			page.save()

			return category(request, category_name_url)
		else:
			print form.errors
	else:
		form = PageForm()

	return render_to_response('mango/add_page.html',{'category_name_url':category_name_url, 'category_name':category_name, 'form':form}, context)





