from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib import admin

from ella.core.box import Box
from ella.core.models import Category, Author, Category, Listing
from ella.core.cache.utils import get_cached_object



class Gallery(models.Model):
    """
    Definition of objects gallery
    """
    # Gallery heading
    title = models.CharField(_('Title'), maxlength=255)
    slug = models.CharField(_('Slug'), maxlength=255)
    # Gallery metadata
    description = models.CharField(_('Description'), maxlength=3000, blank=True)
    owner = models.ForeignKey(Author, verbose_name=_('Gallery owner'), blank=True, null=True)
    category = models.ForeignKey(Category, verbose_name=_('Category'), blank=True, null=True)
    created = models.DateTimeField(_('Created'), default=datetime.now, editable=False)

    @property
    def main_listing(self):
        from ella.core.cache import get_cached_object
        try:
            return get_cached_object(
                    ContentType.objects.get_for_model(Listing),
                    target_ct=ContentType.objects.get_for_model(self.__class__),
                    target_id=self.id,
                    category=self.category
)
        except Listing.DoesNotExist:
            return None

    def get_absolute_url(self):
        listing = self.main_listing
        if listing:
            return listing.get_absolute_url()

    def Box(self, box_type, nodelist):
        return Box(self, box_type, nodelist)

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')

    def __unicode__(self):
        return u'%s gallery' % self.title


class GalleryItem(models.Model):
    """
    Specific object in gallery
    """
    gallery = models.ForeignKey(Gallery, verbose_name=_("Parent gallery"))
    target_ct = models.ForeignKey(ContentType, verbose_name=_('Target content type'))
    target_id = models.IntegerField(_('Target ID'), db_index=True)
    order = models.IntegerField(_('Object order')) # TODO: order with respect to

    @property
    def target(self):
        return get_cached_object(self.target_ct, pk=self.target_id)

    def get_absolute_url(self):
        return '%s%s/%s/' % (self.gallery.get_absolute_url(), ugettext('items'), self.target.slug)

    class Meta:
        ordering = ('order',)
        verbose_name = _('Gallery item')
        verbose_name_plural = _('Gallery items')
        unique_together = (('gallery', 'order',),)


class GalleryItemOptions(admin.ModelAdmin):
    """TODO: pridat widget, ktery bude volat maximuv skript"""
    pass

class GalleryItemTabularOptions(admin.TabularInline):
    pass


class GalleryOptions(admin.ModelAdmin):
    list_display = ('title', 'created', 'category',)
    ordering = ('-slug',)
    fields = (
        (_("Gallery heading"), {'fields': ('title', 'slug',)}),
        (_("Gallery metadata"), {'fields': ('description', 'owner', 'category')}),
)
    list_filter = ('created',)
    search_fields = ('title', 'description',)
    inlines = (GalleryItemTabularOptions(GalleryItem, extra=10),)
    prepopulated_fields = {'slug': ('title',)}



admin.site.register(Gallery, GalleryOptions)
#admin.site.register(GalleryItem, GalleryItemOptions)




from ella.galleries import management

