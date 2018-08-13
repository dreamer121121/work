from django.http import Http404, HttpResponse
import datetime
from django.template.loader import get_template
from django.shortcuts import render_to_response
def hello(request):
    context = {'person_name': 'John Smith', 'company': 'Outdoor Equipment',
                 'ship_date': datetime.date(2009, 4, 2), 'ordered_warranty': False}
    return render_to_response('test.html', context)

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
    return HttpResponse(html)
