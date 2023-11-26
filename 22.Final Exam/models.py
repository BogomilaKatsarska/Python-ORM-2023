from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count


class PublishedOnMixin(models.Model):
    class Meta:
        abstract = True

    published_on = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )


class AuthorManager(models.Manager):
    def get_authors_by_article_count(self):
        return self.annotate(count_articles=Count('articles')).order_by('-count_articles', 'email')


class Author(models.Model):
    full_name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
    )
    email = models.EmailField(
        unique=True,
    )
    is_banned = models.BooleanField(
        default=False,
    )
    birth_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2005),
        ]
    )
    website = models.URLField(
        null=True,
        blank=True,
    )

    objects = AuthorManager()


class Article(PublishedOnMixin):
    class ArticleCategoryChoices(models.TextChoices):
        TECHNOLOGY = 'Technology'
        SCIENCE = 'Science'
        EDUCATION = 'Education'

    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
    )
    content = models.TextField(
        validators=[MinLengthValidator(10)],
    )
    category = models.CharField(
        max_length=10,
        choices=ArticleCategoryChoices.choices,
        default=ArticleCategoryChoices.TECHNOLOGY,
    )
    authors = models.ManyToManyField(
        to=Author,
        related_name='articles',
    )


class Review(PublishedOnMixin):
    content = models.TextField(
        validators=[MinLengthValidator(10)],
    )
    rating = models.FloatField(
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(5.0),
        ]
    )
    author = models.ForeignKey(
        to=Author,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    article = models.ForeignKey(
        to=Article,
        on_delete=models.CASCADE,
        related_name='reviews',
    )