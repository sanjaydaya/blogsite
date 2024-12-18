from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel  # Updated imports
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting  # Updated import

@register_setting
class SocialMediaSettings(BaseSiteSetting):  # Updated class
    """Social media settings for our custom website."""

    facebook = models.URLField(blank=True, null=True, help_text="Facebook URL")
    twitter = models.URLField(blank=True, null=True, help_text="Twitter URL")
    youtube = models.URLField(blank=True, null=True, help_text="YouTube Channel URL")

    panels = [
        MultiFieldPanel([
            FieldPanel("facebook"),
            FieldPanel("twitter"),
            FieldPanel("youtube"),
        ], heading="Social Media Settings")
    ]
