from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel  # Updated import
from wagtail import blocks as streamfield_blocks

from streams import blocks  # Assuming your custom blocks are here

class FlexPage(Page):
    """Flexible page class."""

    template = "flex/flex_page.html"
    subpage_types = ['flex.FlexPage', 'contact.ContactPage']
    parent_page_types = [
        'flex.FlexPage',
        'home.HomePage',
    ]

    content = StreamField(
        [
            ("title_and_text", blocks.TitleAndTextBlock()),
            ("full_richtext", blocks.RichtextBlock()),
            ("simple_richtext", blocks.SimpleRichtextBlock()),
            ("cards", blocks.CardBlock()),
            ("cta", blocks.CTABlock()),
            ("button", blocks.ButtonBlock()),
            ("char_block", streamfield_blocks.CharBlock(
                required=True,
                help_text='Oh wow this is help text!!',
                min_length=10,
                max_length=50,
                template="streams/char_block.html",
            )),
        ],
        null=True,
        blank=True,
    )

    subtitle = models.CharField(max_length=100, null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("content"),  # Updated panel type
    ]

    class Meta:  # noqa
        verbose_name = "Flex Page"
        verbose_name_plural = "Flex Pages"
