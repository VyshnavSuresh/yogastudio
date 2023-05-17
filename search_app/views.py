from django.shortcuts import render
from yogaapp.models import Courses
# Create your views here.
from django.db.models import Q

def SearchResult(request):
    products=None
    query=None
    if 'q' in request.GET:
        query=request.GET.get('q')
        print(query)
        courses=Courses.objects.all().filter(Q(course__icontains = query) | Q(desc__icontains = query))
        return render(request,'search_result.html',{'query':query,'courses':courses})