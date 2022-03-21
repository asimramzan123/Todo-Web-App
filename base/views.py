from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.contrib.auth.mixins import LoginRequiredMixin

from . models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    # not working somehow :)
    # redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')
    
    # only creating new todo for logged in user
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    # redirecting user after login to task list page, even user try to login, register, redirected to taskslist
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self, ).get( *args, **kwargs)
    
    

#Restricting TaskList without user authentication
class TaskList(LoginRequiredMixin ,ListView):
    model = Task
    context_object_name = 'tasks'

    #restricting users to only see their own data
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context['color'] = 'red'
        #making sure that tasks are only users tasks
        context['tasks'] = context['tasks'].filter(user = self.request.user)
        # getting count of Incomplete tasks
        context['count'] = context['tasks'].filter(complete = False).count()
        
        search_input = self.request.GET.get('search-area') or ''
        
        # getting data using condition
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains = search_input)
            # starts with letter searching
            context['tasks'] = context['tasks'].filter(title__startswith = search_input)
            
            
        context['search_input'] = search_input
        
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    
    # only creating new todo for logged in user
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks') 

