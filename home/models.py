from __future__ import unicode_literals

from django.db import models

from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.six import text_type
from django.core.mail import EmailMessage

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, \
    MultiFieldPanel, InlinePanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailsnippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


# Administrator-editable settings

@register_setting
class ImportantLinks(BaseSetting):
    terms_pdf = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    panels = [
        DocumentChooserPanel('terms_pdf'),
    ]


@register_setting
class ContactSettings(BaseSetting):
    address = models.TextField()
    address_uri = models.URLField(blank=True)
    phone_uri = models.URLField(blank=True)
    phone_display = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    github_username = models.CharField(max_length=255, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)

    panels = [
        FieldPanel('address'),
        FieldPanel('phone_uri'),
        FieldPanel('phone_display'),
        FieldPanel('email'),
        FieldPanel('github_username'),
        FieldPanel('twitter_username')
    ]


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
                                  help_text="Optional link titlein this menu "
                                  "(defaults to page title if one exists)")
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
    InlinePanel('menu_items', label="Menu Items"),
]


# Service Price Snippet

@register_snippet
class ServicePrice(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)

    panels = [
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('price'),
    ]

    def __str__(self):
        return self.title


# Testimonial Snippet

@register_snippet
class Testimonial(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_organisation = models.CharField(max_length=100, blank=True)
    customer_job_title = models.CharField(max_length=100, blank=True)
    testimonial = models.TextField()

    panels = [
        FieldPanel('customer_name'),
        FieldPanel('customer_job_title'),
        FieldPanel('customer_organisation'),
        FieldPanel('testimonial'),
    ]

    def __str__(self):
        return self.customer_name


# Home Page

class HomePageFeaturePanel(Orderable):
    page = ParentalKey('home.HomePage', related_name='feature_panels')
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    glyphicon_class = models.CharField(max_length=50)

    panels = [
        FieldPanel('title'),
        FieldPanel('text'),
        FieldPanel('glyphicon_class'),
    ]

    def __str__(self):
        return self.title


class HomePage(Page):

    # Database fields

    subtitle = models.CharField(max_length=255, blank=True)
    body = RichTextField(blank=True)
    pricing_title = models.CharField(max_length=255, blank=True)
    pricing_subtitle = models.CharField(max_length=255, blank=True)
    pricing_footer = RichTextField(blank=True)

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body', classname="full"),
        FieldPanel('pricing_title'),
        FieldPanel('pricing_subtitle'),
        FieldPanel('pricing_footer'),
        InlinePanel('feature_panels', label="Feature Panels"),
    ]


# Standard Page

class StandardPage(Page):

    # Database fields

    subtitle = models.CharField(max_length=255, blank=True)
    body = RichTextField()

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
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


# People Page

PERSON_TEAM_CHOICES = (
    ('technical_team', "Technical Team"),
    ('management_team', "Management Team"),
    ('management_group', "Management Group"),
    ('external_advisory', "External Advisory Board"),
)


class PeoplePagePerson(Orderable):
    page = ParentalKey('home.PeoplePage', related_name='people')
    team = models.CharField(max_length=255, choices=PERSON_TEAM_CHOICES)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True)
    organisation = models.CharField(max_length=255, blank=True)
    short_bio = models.TextField(blank=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('team'),
        FieldPanel('name'),
        FieldPanel('role'),
        FieldPanel('organisation'),
        FieldPanel('short_bio'),
        ImageChooserPanel('photo'),
    ]

    def __str__(self):
        return self.name


class PeoplePage(Page):
    content_panels = Page.content_panels + [
        InlinePanel('people', label="People"),
    ]


# Forms

class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_title = models.CharField(max_length=255)
    thank_you_text = RichTextField(blank=True)

    # Override process_form_submission method to add 'reply-to' header
    def process_form_submission(self, form):
        super(AbstractEmailForm, self).process_form_submission(form)

        if self.to_address:
            content = '\n'.join([x[1].label + ': ' +
                                text_type(form.data.get(x[0]))
                                for x in form.fields.items()])
            reply_to = ([form.data['email']] if 'email' in form.data else None)
            email = EmailMessage(self.subject, content, self.from_address,
                                 [self.to_address], reply_to=reply_to)
            email.send(fail_silently=False)

    # Override serve method to respond with redirect and message
    # rather than landing page
    def serve(self, request):
        if request.method == 'POST':
            form = self.get_form(request.POST)

            if form.is_valid():
                self.process_form_submission(form)

                if request.is_ajax():
                    data = {
                        'message': self.thank_you_title,
                    }
                    return JsonResponse(data)
                else:
                    redirect_path = request.POST.get(
                        "redirect_path", request.path_info)
                    messages.success(request, self.thank_you_title)
                    return HttpResponseRedirect(redirect_path)
            elif request.is_ajax():
                return JsonResponse(form.errors, status=400)

        else:
            form = self.get_form()

        context = self.get_context(request)
        context['form'] = form
        return render(
            request,
            self.template,
            context
        )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('thank_you_title', classname="full"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldPanel('to_address', classname="full"),
            FieldPanel('from_address', classname="full"),
            FieldPanel('subject', classname="full"),
        ], "Email")
    ]
