import pandas as pd
import os
from django.core.management.base import BaseCommand
from myproject.models import Author, Book, Publisher, User, Rating

class Command(BaseCommand):
    help = 'Import data from CSV files into the database using Pandas and bulk_create'

    def handle(self, *args, **kwargs):
        self.import_authors()
        self.stdout.write(self.style.SUCCESS('Authors imported!'))
        self.import_publishers()
        self.stdout.write(self.style.SUCCESS('Publishers imported!'))
        self.import_books()
        self.stdout.write(self.style.SUCCESS('Books imported!'))
        self.import_users()
        self.stdout.write(self.style.SUCCESS('Users imported!'))
        self.import_ratings()
        self.stdout.write(self.style.SUCCESS('Ratings imported!'))

    def import_authors(self):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'authors.csv'))
        authors = [Author(id=row['id'], name=row['name']) for _, row in df.iterrows()]
        Author.objects.bulk_create(authors, ignore_conflicts=True)

    def import_publishers(self):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'publishers.csv'))
        publishers = [Publisher(id=row['id'], name=row['name']) for _, row in df.iterrows()]
        Publisher.objects.bulk_create(publishers, ignore_conflicts=True)

    def import_books(self):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'books.csv'))
        books = []
        for _, row in df.iterrows():
            author = Author.objects.get(id=row['author_id'])
            publisher = Publisher.objects.get(id=row['publisher_id'])
            books.append(Book(
                id=row['id'],
                isbn=row['isbn'],
                title=row['title'],
                year_of_publication=row['year_of_publication'],
                image_url_s=row['image_url_s'],
                image_url_m=row['image_url_m'],
                image_url_l=row['image_url_l'],
                author=author,
                publisher=publisher
            ))
        Book.objects.bulk_create(books, ignore_conflicts=True)

    def import_users(self):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'users.csv'))
        users = []
        for _, row in df.iterrows():
            users.append(User(
                id=row['id'],  # Assuming 'user_id' is the column in the CSV
                age=row['age'] if pd.notna(row['age']) else None,
                city=row['city'],
                state=row['state'] if pd.notna(row['state']) else None,
                country=row['country']
            ))
        User.objects.bulk_create(users, ignore_conflicts=True)

    def import_ratings(self):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'ratings.csv'))
        ratings = []
        for _, row in df.iterrows():
            user = User.objects.get(id=row['user_id'])
            book = Book.objects.get(isbn=row['isbn'])
            ratings.append(Rating(
                id=row['id'],
                user=user,
                book=book,
                book_rating=row['book_rating']
            ))
        Rating.objects.bulk_create(ratings, ignore_conflicts=True)
