from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from json_field import JSONField
from model_utils.models import StatusModel, TimeStampedModel
from taggit.managers import TaggableManager

from users.models import User
from lib.storage import upload_path
from . import choices


class Article(StatusModel, TimeStampedModel):

    def upload_article_callback(self, path, filename):
        return upload_path('articles', filename)

    def upload_materials_callback(self, filename):
        return upload_path('materials', filename)

    site_owner = models.ForeignKey(User, verbose_name=_(u'Compendia Owner'))
    authorship = JSONField(blank=True, verbose_name=_(u'Authors'))
    contributors = models.ManyToManyField(User, through='Contributor', related_name='contributors',
        help_text=_(u'Users who have contributed to this compendium'))
    STATUS = choices.STATUS
    doi = models.CharField(max_length=2000, verbose_name=_(u'DOI (optional)'), blank=True)
    title = models.CharField(max_length=500, verbose_name=_(u'Title'))
    paper_abstract = models.TextField(max_length=5000, blank=True)
    journal = models.CharField(blank=True, max_length=500, verbose_name=_(u'Journal Name (if applicable)'))
    article_url = models.URLField(blank=True, max_length=2000, verbose_name=_(u'Article URL'))
    related_urls = JSONField(blank=True, verbose_name=_(u'Related URLs'))
    primary_research_field = models.CharField(max_length=300, choices=choices.RESEARCH_FIELDS,
        verbose_name=_(u'Primary research field'), blank=True)
    secondary_research_field = models.CharField(max_length=300, choices=choices.RESEARCH_FIELDS,
        verbose_name=_(u'Secondary research field'), blank=True)
    notes_for_staff = models.TextField(max_length=5000, blank=True, verbose_name=_(u'Notes for staff'),
        help_text=_(u'Private notes to the staff for help in creating your research'
                    u'compendium, including links to data and code if not uploaded'))
    article_file = models.FileField(blank=True, upload_to=upload_article_callback, help_text=_(u'File containing the article (optional)'))
    code_archive_file = models.FileField(blank=True, upload_to=upload_materials_callback, help_text=_(u'File containing an archive of the code'))
    data_archive_file = models.FileField(blank=True, upload_to=upload_materials_callback, help_text=_(u'File containing an archive of the data'))
    tags = TaggableManager(blank=True)
    legacy_id = models.IntegerField(blank=True, null=True, verbose_name=_(u'RunMyCode ID'), help_text=_(u'Only used for old RunMyCode pages'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('compendium', args=(self.id,))

    class Meta(object):
        ordering = ['title']
        verbose_name = _(u'compendium')
        verbose_name_plural = _(u'compendia')


class Contributor(TimeStampedModel):
    user = models.ForeignKey(User, verbose_name=(u'Contributing User'))
    article = models.ForeignKey(Article, verbose_name=_(u'Article'))
    role = models.CharField(max_length=50, choices=choices.CONTRIBUTOR_ROLES,
        verbose_name=_(u'Contributing Role'),
        blank=True)
    citation_order = models.IntegerField(blank=True, null=True, verbose_name=_(u'Citation Order'))

    def __unicode__(self):
        return '%s contributor for %s' % (self.user, self.article)

    class Meta(object):
        ordering = ['citation_order', 'user']
        verbose_name = _(u'contributor')
        verbose_name_plural = _(u'contributors')
