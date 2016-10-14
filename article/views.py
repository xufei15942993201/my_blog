# -*- coding: utf-8 -*-
from django.shortcuts import render,redirect,render_to_response,HttpResponseRedirect
from form import RegisterForm,LoginForm,ChangepwdForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.http import HttpResponse
from article.models import Article
from datetime import datetime
from django.http import Http404
from django.contrib.syndication.views import Feed
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  #添加包
from django.contrib.auth.decorators import login_required
# Create your views here.
#登录
def register(request):
    error=[]
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            email = data['email']
            password = data['password']
            password2= data['password2']
            if not User.objects.all().filter(username=username):
                if form.pwd_validate(password, password2):
                    user = User.objects.create_user(username, email, password)
                    user.save()
                    login_validate(request,username,password)
                    return render_to_response('home.html',{'user':username})
                else:
                    error.append('Please input the same password')
            else:
                error.append('The username has existed,please change your username')
    else:
        form = RegisterForm()
    return render_to_response('register.html',{'form':form,'error':error})
def login_validate(request,username,password):
    rtvalue = False
    user = authenticate(username=username,password=password)
    if user is not None:
        if user.is_active:
            auth_login(request,user)
            return True
    return rtvalue
def homepage(request):
    return HttpResponse("Welcome to Homepage!")
def mylogin(request):
    error = []
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            if login_validate(request,username,password):
                return render_to_response('home.html',{'user':username})
            else:
                error.append('Please input the correct password')
        else:
            error.append('Please input both username and password')
    else:
        form = LoginForm()
    return render_to_response('login.html',{'error':error,'form':form})
def mylogout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')
def home(request):
    posts = Article.objects.all()  #获取全部的Article对象
    paginator = Paginator(posts, 5) #每页显示两个
    page = request.GET.get('page')
    try :
        post_list = paginator.page(page)
    except PageNotAnInteger :
        post_list = paginator.page(1)
    except EmptyPage :
        post_list = paginator.paginator(paginator.num_pages)
    return render(request, 'home.html', {'post_list' : post_list})

def detail(request, id):
    try:
        post = Article.objects.get(id=str(id))
    except Article.DoesNotExist:
        raise Http404
    return render(request, 'post.html', {'post' : post})

def archives(request) :
    try:
        post_list = Article.objects.all()
    except Article.DoesNotExist :
        raise Http404
    return render(request, 'archives.html', {'post_list' : post_list,
                                            'error' : False})
@login_required
def about_me(request) :
    return render(request, 'aboutme.html')

def search_tag(request, tag) :
    try:
        post_list = Article.objects.filter(category__iexact = tag) #contains
    except Article.DoesNotExist :
        raise Http404
    return render(request, 'tag.html', {'post_list' : post_list})

def blog_search(request):
    if 's' in request.GET:
        s = request.GET['s']
        if not s:
            return render(request,'home.html')
        else:
            post_list = Article.objects.filter(title__icontains = s)
            if len(post_list) == 0 :
                return render(request,'archives.html', {'post_list' : post_list,
                                                    'error' : True})
            else :
                return render(request,'archives.html', {'post_list' : post_list,
                                                    'error' : False})
    return redirect('/')

class RSSFeed(Feed) :
    title = "RSS feed - article"
    link = "feeds/posts/"
    description = "RSS feed - blog posts"

    def items(self):
        return Article.objects.order_by('-date_time')

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.date_time

    def item_description(self, item):
        return item.content
