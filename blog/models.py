from django.db import models
from django import forms
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from rest_framework.fields import Field
from wagtail.api import APIField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.models import Page, Orderable
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache  # Import for cache handling

# Custom Fields
class ImageSerializedField(Field):
    """A custom serializer used in Wagtail's API."""
    
    def to_representation(self, value):
        return {
            "url": value.file.url,
            "title": value.title,
            "width": value.width,
            "height": value.height,
        }

# Custom Block
from wagtail import blocks

class TitleAndTextBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Add your title")
    text = blocks.TextBlock(required=True, help_text="Add additional text")

    class Meta:
        template = "streams/title_and_text_block.html"
        icon = "edit"
        label = "Title & Text"

# Snippet Models for Blog Author and Category
class BlogAuthor(models.Model):
    """Blog Author snippet."""
    name = models.CharField(max_length=100)
    website = models.URLField(blank=True, null=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="+",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("image"),
            ],
            heading="Author Details"
        ),
        FieldPanel("website"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Blog Author"
        verbose_name_plural = "Blog Authors"

register_snippet(BlogAuthor)

class BlogCategory(models.Model):
    """Blog Category snippet."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, allow_unicode=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"

    def __str__(self):
        return self.name

register_snippet(BlogCategory)

# Blog Models
class BlogChildPagesSerializer(Field):
    """Serializer for blog child pages."""
    def to_representation(self, child_pages):
        return [{
            'id': child.id,
            'title': child.title,
            'slug': child.slug,
            'url': child.url,
        } for child in child_pages]

class BlogListingPage(RoutablePageMixin, Page):
    """Page listing all blog posts."""
    template = "blog/blog_listing_page.html"
    max_count = 1
    subpage_types = ['blog.VideoBlogPage', 'blog.ArticleBlogPage']

    custom_title = models.CharField(max_length=100)

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
    ]

    api_fields = [
        APIField("posts", serializer=BlogChildPagesSerializer(source='get_child_pages')),
    ]

    @property
    def get_child_pages(self):
        return self.get_children().public().live()

    def get_context(self, request, *args, **kwargs):
        """Custom context for the blog listing page."""
        context = super().get_context(request, *args, **kwargs)
        posts = BlogDetailPage.objects.live().public().order_by('-first_published_at')

        if request.GET.get('tag', None):
            tag = request.GET['tag']
            posts = posts.filter(tags__slug=tag)

        paginator = Paginator(posts, 2)
        page = request.GET.get("page")
        try:
            context['posts'] = paginator.page(page)
        except PageNotAnInteger:
            context['posts'] = paginator.page(1)
        except EmptyPage:
            context['posts'] = paginator.page(paginator.num_pages)

        context['categories'] = BlogCategory.objects.all()
        return context

    @route(r"^category/(?P<cat_slug>[-\w]+)/$", name="category_view")
    def category_view(self, request, cat_slug):
        """View blog posts by category."""
        context = self.get_context(request)

        try:
            category = BlogCategory.objects.get(slug=cat_slug)
        except BlogCategory.DoesNotExist:
            category = None

        if category:
            context['posts'] = BlogDetailPage.objects.live().public().filter(categories=category)
        else:
            context['posts'] = BlogDetailPage.objects.none()

        return render(request, "blog/latest_posts.html", context)

    def get_sitemap_urls(self, request):
        """Generate sitemap for the blog listing page."""
        sitemap = super().get_sitemap_urls(request)
        sitemap.append({
            "location": self.full_url + self.reverse_subpage("latest_posts"),
            "lastmod": self.last_published_at or self.latest_revision_created_at,
            "priority": 0.9,
        })
        return sitemap

class BlogDetailPage(Page):
    """Detail page for a blog post."""
    subpage_types = []
    parent_page_types = ['blog.BlogListingPage']
    tags = ClusterTaggableManager(through='blog.BlogPageTag', blank=True)

    custom_title = models.CharField(max_length=100)
    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)

    banner_image = StreamField([("image", ImageChooserBlock())], blank=True, null=True)
    content = StreamField([
        ("title_and_text", TitleAndTextBlock()),  # Use the custom block here
        ("full_richtext", blocks.RichTextBlock()),
        ("image", ImageChooserBlock()),
    ], blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("custom_title"),
        FieldPanel("tags"),
        FieldPanel("banner_image"),
        MultiFieldPanel([ 
            InlinePanel("blog_authors", label="Author", min_num=1, max_num=4)
        ], heading="Authors"),
        MultiFieldPanel([FieldPanel("categories", widget=forms.CheckboxSelectMultiple)], heading="Categories"),
        FieldPanel("content"),
    ]

    api_fields = [
        APIField("tags"),
        APIField("content"),
    ]

    def save(self, *args, **kwargs):
        """Custom save method to clear cache for blog preview."""
        key = f"blog_post_preview_{self.id}"  # Custom cache key
        cache.delete(key)
        super().save(*args, **kwargs)

class ArticleBlogPage(BlogDetailPage):
    """Blog post page for articles."""
    template = "blog/article_blog_page.html"
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    intro_image = StreamField([("image", ImageChooserBlock())], blank=True, null=True)

    content_panels = BlogDetailPage.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("intro_image"),
    ]

class VideoBlogPage(BlogDetailPage):
    """Blog post page for videos."""
    template = "blog/video_blog_page.html"
    video_url = models.URLField(blank=True, null=True)

    content_panels = BlogDetailPage.content_panels + [
        FieldPanel("video_url"),
    ]
