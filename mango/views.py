from django.http import HttpResponseRedirect ,HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from mango.models import Category, Page
from mango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from mango.bing_search import run_query
import re
from django.db.models import Q
from mango.music_search import music_query


category_list = Category.objects.order_by('-likes')[:5]
page_list = Page.objects.order_by('-views')[:5]
cat_list = Category.objects.order_by('name')

def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
	return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
	query = None # Query to search for every search term        
	terms = normalize_query(query_string)
	for term in terms:
		or_query = None # Query to search for a given term in each field
		for field_name in search_fields:
			q = Q(**{"%s__icontains" % field_name: term})
			if or_query is None:
				or_query = q
			else:
				or_query = or_query | q
		if query is None:
			query = or_query
		else:
			query = query & or_query
		return query



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
	context_dict = {'categories': category_list,'pages': page_list,'cat_list':cat_list}
	for category in category_list:
		category.url = encdec(category.name,'encode')
	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits',0)

		if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days>0:
			request.session['last_visit'] = str(datetime.now())
			request.session['visits'] = visits+1
	else:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1

		
	return render_to_response('mango/index.html',context_dict,context)

def about(request):
	context = RequestContext(request)

	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0

	return render_to_response('mango/about.html', {'visits':count,'cat_list':cat_list}, context)


def category(request,category_name_url):
	context = RequestContext(request)
	category_name = encdec(category_name_url,'decode')
	context_dict = {'category_name': category_name}
	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category).order_by('-views')
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_url'] = category_name_url
		context_dict['cat_list'] = cat_list
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

	return render_to_response('mango/add_category.html', {'form':form,'cat_list':cat_list},context)

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

	return render_to_response('mango/add_page.html',{'category_name_url':category_name_url, 'category_name':category_name, 'form':form, 'cat_list':cat_list}, context)

def register(request):
	context = RequestContext(request)
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
			user.backend = 'django.contrib.auth.backends.ModelBackend'
			login(request, user)
			return render_to_response('mango/index.html',{'registered':registered, 'categories': category_list,'pages': page_list, 'cat_list':cat_list}, context)

		else:
			print user_form.errors, profile_form.errors

	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render_to_response('mango/register.html',{'user_form':user_form, 'profile_form':profile_form, 'registered':registered, 'cat_list':cat_list}, context)


def user_login(request):
	context = RequestContext(request)
	context_dict ={'cat_list':cat_list}
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request,user)
				return HttpResponseRedirect('/mango/')
			else:
				context_dict['disabled_account'] = True
				return HttpResponse("Your mango account is disabled")

		else:
			print "Invalid login details: {0},{1}".format(username,password)
			context_dict['bad_details'] = True
			return render_to_response('mango/login.html',context_dict,context)
			#return HttpResponse("Invalid login details supplied")
	else:
		return render_to_response('mango/login.html',{'cat_list':cat_list},context)

@login_required
def restricted(request):
	return HttpResponse("Since you're not logged in you cannot see this text")

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/mango/')

def search(request):
	context = RequestContext(request)
	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			if 'App_Search' in request.POST:
				entry_query = get_query(query,['title','url'])
				result_list = Page.objects.filter(entry_query).order_by('-id')
			else:
				result_list = run_query(query)

	return render_to_response('mango/search.html',{'result_list':result_list, 'cat_list':cat_list },context)

def track_url(request):
	context = RequestContext(request)
	page_id = None
	url = '/mango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views+1
				page.save()
				url = page.url
			except:
				pass

	return redirect(url)

def song_search(request):
	context = RequestContext(request)
	result_list = []
	if request.method == 'POST':
		mquery = request.POST['mquery'].strip()
		if mquery:
			result_list = music_query(mquery)

	return render_to_response('mango/music_search.html',{'result_list':result_list},context)







