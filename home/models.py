from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey

from wagtail.api import APIField
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
    PageChooserPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from rest_framework.fields import Field

from streams import blocks


class HomePageCarouselImages(Orderable):
    page = ParentalKey("home.HomePage", related_name="carousel_images")
    carousel_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [FieldPanel("carousel_image")]
    api_fields = [APIField("carousel_image")]


class BannerCTASerializer(Field):
    def to_representation(self, page):
        return {
            'id': page.id,
            'title': page.title,
            'first_published_at': page.first_published_at,
            'owner': page.owner.username if page.owner else None,
            'slug': page.slug,
            'url': page.url,
        }


class HomePage(RoutablePageMixin, Page):
    template = "home/home_page.html"
    subpage_types = ['blog.BlogListingPage', 'contact.ContactPage', 'flex.FlexPage']
    parent_page_type = ['wagtailcore.Page']

    banner_title = models.CharField(max_length=100, blank=False, null=True)
    banner_subtitle = RichTextField(features=["bold", "italic"])
    banner_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    banner_cta = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content = StreamField([("cta", blocks.CTABlock())], null=True, blank=True)

    api_fields = [
        APIField("banner_title"),
        APIField("banner_subtitle"),
        APIField("banner_image"),
        APIField("banner_cta", serializer=BannerCTASerializer()),
        APIField("carousel_images"),
        APIField("content"),
        APIField("a_custom_api_response"),
    ]

    @property
    def a_custom_api_response(self):
        return f"Banner Title Is: {self.banner_title}"

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [InlinePanel("carousel_images", max_num=5, min_num=1, label="Image")],
            heading="Carousel Images",
        ),
        FieldPanel("content"),
    ]

    banner_panels = [
        MultiFieldPanel(
            [
                FieldPanel("banner_title"),
                FieldPanel("banner_subtitle"),
                FieldPanel("banner_image"),
                PageChooserPanel("banner_cta"),
            ],
            heading="Banner Options",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading='Content'),
            ObjectList(banner_panels, heading="Banner Settings"),
            ObjectList(Page.promote_panels, heading='Promotional Stuff'),
            ObjectList(Page.settings_panels, heading='Settings Stuff'),
        ]
    )

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Pages"

    @route(r'^subscribe/$')
    def the_subscribe_page(self, request, *args, **kwargs):
        context = self.get_context(request, *args, **kwargs)
        return render(request, "home/subscribe.html", context)

    def get_admin_display_title(self):
        return "Custom Home Page Title"
