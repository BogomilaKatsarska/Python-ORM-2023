from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Count


class Person(models.Model):
    class Meta:
        abstract = True

    full_name = models.CharField(
        max_length=120,
        validators=[MinLengthValidator(2)],
    )
    birth_date = models.DateField(
        default='1900-01-01',
    )
    nationality = models.CharField(
        max_length=50,
        default='Unknown',
    )


class Awarded(models.Model):
    class Meta:
        abstract = True
    is_awarded = models.BooleanField(
        default=False,
    )


class TimestampModel(models.Model):
    class Meta:
        abstract = True

    last_updated = models.DateTimeField(
        auto_now=True,
    )


class DirectorManager(models.Manager):

    def get_directors_by_movies_count(self):
        return self.annotate(num_movies=Count('movies')).order_by('-num_movies', 'full_name')


class Director(Person):
    years_of_experience = models.SmallIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
    )
    objects = DirectorManager()

    def __str__(self):
        return f"Director: {self.full_name}"


class Actor(Person, Awarded, TimestampModel):
    def __str__(self):
        return f"Actor: {self.full_name}"


class Movie(Awarded, TimestampModel):
    class GenreChoices(models.TextChoices):
        ACTION = 'Action'
        COMEDY = 'Comedy'
        DRAMA = 'Drama'
        OTHER = 'Other'

    title = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(5)],
    )
    release_date = models.DateField()
    storyline = models.TextField(
        null=True,
        blank=True,
    )
    genre = models.CharField(
        max_length=6,
        default=GenreChoices.OTHER,
        choices=GenreChoices.choices,
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        default=0.0,
    )
    is_classic = models.BooleanField(
        default=False,
    )
    director = models.ForeignKey(
        to=Director,
        on_delete=models.CASCADE,
        related_name='movies',
    )
    starring_actor = models.ForeignKey(
        to=Actor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movies'
    )
    actor = models.ManyToManyField(
        to=Actor,
    )

    def __str__(self):
        return f"Movie: {self.title}"
