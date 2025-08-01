from django.contrib import messages
from datetime import date
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from .models import Todo
from .forms import TodoForm
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.db import models

# Create your views here.

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'todo/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'todo/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@never_cache
def home(request):
    filter_option = request.GET.get('filter', 'all')

    # Check if user is authenticated
    if request.user.is_authenticated:
        todos = Todo.objects.filter(user=request.user)

        # Apply filter
        if filter_option == 'completed':
            todos = todos.filter(completed=True)
        elif filter_option == 'pending':
            todos = todos.filter(completed=False)

        # Priority sorting
        priority_order = models.Case(
            models.When(priority='H', then=0),
            models.When(priority='M', then=1),
            models.When(priority='L', then=2),
            default=3,
            output_field=models.IntegerField(),
        )

        todos = todos.annotate(
            safe_due_date=Coalesce('due_date', Value(date(9999, 12, 31)))
        ).order_by('completed', priority_order, 'safe_due_date', 'title')

        if request.method == 'POST':
            form = TodoForm(request.POST)
            if form.is_valid():
                new_todo = form.save(commit=False)
                new_todo.user = request.user
                new_todo.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    todos = Todo.objects.filter(user=request.user)

                    if filter_option == 'completed':
                        todos = todos.filter(completed=True)
                    elif filter_option == 'pending':
                        todos = todos.filter(completed=False)

                    todos = todos.annotate(
                        safe_due_date=Coalesce('due_date', Value(date(9999, 12, 31)))
                    ).order_by('completed', priority_order, 'safe_due_date', 'title')

                    html = render_to_string('todo/partials/todo_list.html', {'todos': todos, 'request': request})
                    return JsonResponse({'success': True, 'html': html, 'message': '✅ Task added successfully'})
        else:
            form = TodoForm()

    else:
        # Anonymous session-based todos
        todos = request.session.get('todos', [])

        if request.method == 'POST':
            form = TodoForm(request.POST)
            if form.is_valid():
                new_todo = {
                    'title': form.cleaned_data['title'],
                    'completed': False,
                    'priority': form.cleaned_data['priority'],
                    'due_date': form.cleaned_data['due_date'].isoformat() if form.cleaned_data['due_date'] else None
                }
                todos.append(new_todo)
                request.session['todos'] = todos
                messages.success(request, '✅ Task added (guest mode)')
                return redirect('home')
        else:
            form = TodoForm()

    return render(request, 'todo/home.html', {
        'todos': todos,
        'form': form,
        'filter': filter_option,
        'is_guest': not request.user.is_authenticated,
    })

@require_POST
@login_required
def toggle_complete(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id)
    todo.completed = not todo.completed
    todo.save()
    return JsonResponse({'id': todo_id, 'completed': todo.completed})

@require_POST
@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        todo.delete()
        return JsonResponse({'success': True, 'id': todo_id, 'message': '🗑️ Task deleted successfully'})
    todo.delete()
    messages.warning(request, '🗑️ Task deleted successfully')
    return redirect('home')

@never_cache
@login_required
def edit_todo(request, todo_id):
    if not request.user.is_authenticated:
        messages.error(request, "🔒 Please log in to edit your saved tasks.")
        return redirect('home')
    todo = get_object_or_404(Todo, pk=todo_id, user=request.user)

    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Task updated successfully')
            return redirect('home')
    else:
        form = TodoForm(instance=todo)

    return render(request, 'todo/edit.html', {
        'form': form,
        'todo': todo
    })