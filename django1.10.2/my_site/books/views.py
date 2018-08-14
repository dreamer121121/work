from django.shortcuts import render
from django.http import HttpResponse
from .import models


def search(request):
    errors = []
    if 'q' in request.GET:  # 检查q是否存在于且q的值不能为空
        q = request.GET['q']
        if not q:
            errors.append('Enter a search term')
        elif len(q) > 20:
            errors.append('Please enter at most 20 characters.')
        else:
            books = models.Book.objects.filter(title__icontains=q)
            return render(request, 'search_result.html', {'books': books})

    return render(request, 'search_form.html', {'errors': errors})


def contact(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('subject', ''):
            errors.append('Enter a subject.')
        if not request.POST.get('message', ''):
            errors.append('Enter a message.')
        if request.POST.get('email') and '@' not in request.POST['email']:
            errors.append('Enter a valid e-mail address.')
        if not errors:
            send_mail(
                request.POST['subject'],
                request.POST['message'],
                request.POST.get('email', 'noreply@example.com'),
                ['siteowner@example.com'],
            )
            return HttpResponseRedirect('/contact/thanks/')
    return render('contact_form.html', {'errors': errors})
