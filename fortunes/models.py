from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from fortunes.managers import FortuneManager

class Fortune(models.Model):
    author = models.CharField(max_length=45, blank=False)
    title = models.CharField(max_length=200, blank=False)
    slug = models.SlugField(_('slug'), db_index=True, max_length=255, unique_for_date='pub_date')
    content = models.TextField(blank=False)
    pub_date = models.DateTimeField(_('published date'), default=datetime.now())
    votes = models.IntegerField(default=0)

    objects = FortuneManager()

    def __unicode__(self):
        return _("%s, from %s") % (self.title, self.author)

    def check_slug(self):
        "If no slug has been generated yet, tries to generate a unique one"
        if not self.slug:
            prefix = ""
            i = 0
            while True:
                self.slug = prefix + slugify(self.title)
                try:
                    Fortune.objects.values('id').get(slug=self.slug)
                    i += 1
                    prefix = str(i) + "-"
                except Fortune.DoesNotExist:
                    break
        return self.slug

    @models.permalink
    def get_absolute_url(self):
        return ('fortune_detail', (), {
            'slug': self.slug,
            'year': self.pub_date.year,
            'month': self.pub_date.month,
            'day': self.pub_date.day
        })

    def save(self):
        self.check_slug()
        super(Fortune, self).save()