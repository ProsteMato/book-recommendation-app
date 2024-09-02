from django.db import models

class Author(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Book(models.Model):
    id = models.IntegerField(primary_key=True)
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    year_of_publication = models.IntegerField()
    image_url_s = models.URLField()
    image_url_m = models.URLField()
    image_url_l = models.URLField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'User {self.id}'

class Rating(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    book_rating = models.PositiveIntegerField()

    def __str__(self):
        return f'Rating {self.book_rating} for {self.book.title} by User {self.user.id}'
