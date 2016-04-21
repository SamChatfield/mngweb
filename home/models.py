from __future__ import unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, \
    MultiFieldPanel, InlinePanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


# A couple of abstract classes that contain commonly used fields

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class ContactFields(models.Model):
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    post_code = models.CharField(max_length=10, blank=True)

    panels = [
        FieldPanel('telephone'),
        FieldPanel('email'),
        FieldPanel('address_1'),
        FieldPanel('address_2'),
        FieldPanel('city'),
        FieldPanel('country'),
        FieldPanel('post_code'),
    ]

    class Meta:
        abstract = True


# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Related links

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Menus

class NavigationMenuItem(Orderable, LinkFields):
    menu = ParentalKey(to='home.NavigationMenu', related_name='menu_items')
    menu_title = models.CharField(max_length=255, blank=True,
                                  help_text="Optional link title in this menu \
                                  (defaults to page title if one exists)")
    css_class = models.CharField(max_length=255, blank=True,
                                 verbose_name="CSS Class",
                                 help_text="Optional styling")

    @property
    def title(self):
        if self.menu_title:
            return self.menu_title

        if self.link_page:
            return self.link_page.title
        elif self.link_document:
            return self.link_document.title
        else:
            return self.link_external

    @property
    def url(self):
        return self.link

    def __str__(self):
        return self.title

    panels = LinkFields.panels + [
        FieldPanel('menu_title'),
        FieldPanel('css_class')
    ]


class NavigationMenuManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(menu_name=name)


@register_snippet
class NavigationMenu(ClusterableModel):
    objects = NavigationMenuManager()
    menu_name = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.menu_name

NavigationMenu.panels = [
    FieldPanel('menu_name', classname='full title'),
    InlinePanel('menu_items', label="Menu Items")
]


# Home Page

class HomePage(Page):

    # Database fields

    body = RichTextField(blank=True)

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]


# Standard Page

class StandardPage(Page):

    # Database fields

    body = RichTextField()

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]


# News Page

class NewsPage(Page):

    # Database fields

    body = RichTextField()
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # Editor panels configuration

    conent_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('body', classname="full"),
    ]

    promote_panels = [
        ImageChooserPanel('feed_image'),
    ]
