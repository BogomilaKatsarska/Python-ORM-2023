import os
import django
from django.db.models import Q, Count, Avg

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orm_skeleton.settings")
django.setup()

from main_app.models import Author, Article, Review


def get_authors(search_name=None, search_email=None):
    if search_name is None and search_email is None:
        return ""

    query = Q()
    query_name = Q(full_name__icontains=search_name)
    query_email = Q(email__icontains=search_email)
    if search_name and search_email:
        query = query_name & query_email
    elif search_name:
        query = query_name
    else:
        query = query_email

    authors = Author.objects.filter(query).order_by('-full_name')

    if not authors:
        return ""
    result = []

    for author in authors:
        if author.is_banned:
            ban_status = 'Banned'
        else:
            ban_status = 'Not Banned'
        result.append(
            f"Author: {author.full_name}, email: {author.email}, status: {ban_status}")

    return "\n".join(result)


def get_top_publisher():
    top_publisher = Author.objects.get_authors_by_article_count().first()

    if not Article.objects.all().exists():
        return ""

    return f"Top Author: {top_publisher.full_name} with {top_publisher.count_articles} published articles."


def get_top_reviewer():
    top_reviewer = Author.objects.annotate(count_reviews=Count('reviews')).filter(count_reviews__gt=0).order_by('-count_reviews', 'email').first()

    # if top_reviewer.count_reviews is None:
    if not Review.objects.all().exists():
        return ""

    return f"Top Reviewer: {top_reviewer.full_name} with {top_reviewer.count_reviews} published reviews."

#Django Queries II:


def get_latest_article():
    last_published_article = Article.objects.prefetch_related('reviews').annotate(count_reviews=Count('reviews'), avg_rating=Avg('reviews__rating')).order_by('-published_on').first()

    if not Article.objects.all().exists():
        return ""

    all_authors = ", ".join([author.full_name for author in last_published_article.authors.order_by('full_name')])
    if last_published_article.count_reviews is None:
        result = 0
    else:
        result = last_published_article.count_reviews

    return f"The latest article is: {last_published_article.title}. Authors: {all_authors}. Reviewed: {result} times. Average Rating: {last_published_article.avg_rating:.2f}."


def get_top_rated_article():
    top_rated_article = Article.objects.annotate(count_reviews=Count('reviews'), avg_rating=Avg('reviews__rating')).filter(count_reviews__gt=0).order_by('-avg_rating','title').first()

    if not Review.objects.all().exists():
        return ""
    return f"The top-rated article is: {top_rated_article.title}, with an average rating of {top_rated_article.avg_rating:.2f}, reviewed {top_rated_article.count_reviews} times."


def ban_author(email=None):
    author_to_be_banned = Author.objects.annotate(count_reviews=Count('reviews')).filter(email__exact=email)

    if not author_to_be_banned or email is None or not Author.objects.all().exists():
        return "No authors banned."

    author_to_be_banned.update(is_banned=True)
    author_to_be_banned.save()
    Review.objects.filter(author=author_to_be_banned.pk).delete()

    return f"Author: {author_to_be_banned.full_name} is banned! {author_to_be_banned.count_reviews} reviews deleted."
