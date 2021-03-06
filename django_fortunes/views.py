from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.conf import settings
from django.views.generic import date_based, list_detail
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from django_fortunes.models import Fortune
from django_fortunes.forms import PublicFortuneForm

def fortune_detail(request, year, month, day, slug,
                   template_name='detail.html', template_object_name='fortune',
                   **kwargs):
    '''
    Display one fortune, and provides a comment form wich will
    be handled and persisted if request is POST
    '''
    return date_based.object_detail(
      request,
      year = year,
      month = month,
      day = day,
      date_field = 'pub_date',
      slug = slug,
      queryset = Fortune.objects.published(),
      month_format = '%m',
      template_object_name = template_object_name,
      template_name = template_name,
      **kwargs
    )

def fortune_list(request, order_type='latest', author=None, template_name='index.html',
                 template_object_name='fortune', **kwargs):
    '''
    Lists Fortunes
    '''
    
    extra = {}
    
    # Filtering
    if author:
        queryset = Fortune.objects.latest_by_author(author)
        extra['author'] = author
    else:
        queryset = Fortune.objects.latest()
    
    # Ordering
    if order_type == 'top':
        queryset = queryset.order_by('-votes')
    elif order_type == 'worst':
        queryset = queryset.order_by('votes')
    else:
        # latest
        queryset = queryset.order_by('-pub_date')
    
    extra['order_type'] = order_type
    
    return list_detail.object_list(
      request,
      queryset = queryset,
      paginate_by = getattr(settings, 'FORTUNES_MAX_PER_PAGE', 3),
      template_name = template_name,
      template_object_name = template_object_name,
      extra_context = extra,
      **kwargs
    )

@login_required
def fortune_new(request, template_name='new.html'):
    '''
    Provides a Fortune creation form, validates the form if values posted 
    and saves a new Fortune in the database if everything's okay
    '''
    if request.method == 'POST':
        form = PublicFortuneForm(request.POST)
        if form.is_valid():
            fortune = form.save(commit=False)
            fortune.author = request.user
            fortune.save()
            return redirect(fortune)
    else:
        form = PublicFortuneForm()
    return render_to_response(template_name,
                              {'form': form, 'section': 'new'},
                              context_instance=RequestContext(request))

def fortune_vote(request, object_pk, direction):
    '''
    Votes up or down a fortune
    '''
    fortune = get_object_or_404(Fortune, pk=object_pk)
    fortune.votes += 1 if direction == 'up' else -1
    fortune.save()
    
    return redirect(fortune)
