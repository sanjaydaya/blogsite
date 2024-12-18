"""Streamfields live in here."""

from wagtail.blocks import (
    StructBlock, 
    CharBlock, 
    TextBlock, 
    ListBlock, 
    PageChooserBlock, 
    URLBlock, 
    RichTextBlock, 
    StructValue
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.templatetags.wagtailcore_tags import richtext


class TitleAndTextBlock(StructBlock):
    """Title and text block."""

    title = CharBlock(required=True, help_text="Add your title")
    text = TextBlock(required=True, help_text="Add additional text")

    class Meta:  # noqa
        template = "streams/title_and_text_block.html"
        icon = "edit"
        label = "Title & Text"


class CardBlock(StructBlock):
    """Cards with an image, title, text, and optional button(s)."""

    title = CharBlock(required=True, help_text="Add your title")
    cards = ListBlock(
        StructBlock(
            [
                ("image", ImageChooserBlock(required=True)),
                ("title", CharBlock(required=True, max_length=40)),
                ("text", TextBlock(required=True, max_length=200)),
                ("button_page", PageChooserBlock(required=False)),
                (
                    "button_url",
                    URLBlock(
                        required=False,
                        help_text="If the button page above is selected, it will take precedence.",
                    ),
                ),
            ]
        )
    )

    class Meta:  # noqa
        template = "streams/card_block.html"
        icon = "placeholder"
        label = "Staff Cards"


class RichtextBlock(RichTextBlock):
    """Richtext block with all features."""

    def get_api_representation(self, value, context=None):
        """Return the raw HTML representation for API usage."""
        return richtext(value.source)

    class Meta:  # noqa
        template = "streams/richtext_block.html"
        icon = "doc-full"
        label = "Full RichText"


class SimpleRichtextBlock(RichTextBlock):
    """Richtext block with limited features."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.features = ["bold", "italic", "link"]

    class Meta:  # noqa
        template = "streams/richtext_block.html"
        icon = "edit"
        label = "Simple RichText"


class CTABlock(StructBlock):
    """Call-to-action block."""

    title = CharBlock(required=True, max_length=60)
    text = RichTextBlock(required=True, features=["bold", "italic"])
    button_page = PageChooserBlock(required=False)
    button_url = URLBlock(required=False)
    button_text = CharBlock(required=True, default='Learn More', max_length=40)

    class Meta:  # noqa
        template = "streams/cta_block.html"
        icon = "placeholder"
        label = "Call to Action"


class LinkStructValue(StructValue):
    """Custom logic for handling URLs."""

    def url(self):
        """Determine the URL to use based on available fields."""
        button_page = self.get('button_page')
        button_url = self.get('button_url')
        if button_page:
            return button_page.url
        if button_url:
            return button_url
        return None


class ButtonBlock(StructBlock):
    """A block for a single button with an external or internal URL."""

    button_page = PageChooserBlock(
        required=False, 
        help_text="If selected, this URL will be used first"
    )
    button_url = URLBlock(
        required=False, 
        help_text="If added, this URL will be used if no button page is selected"
    )

    class Meta:  # noqa
        template = "streams/button_block.html"
        icon = "placeholder"
        label = "Single Button"
        value_class = LinkStructValue
