import pandas as pd
import os
from django.core.management.base import BaseCommand
from myproject.models import Author, Book, Publisher, User, Rating
from sqlalchemy import create_engine
from django.conf import settings

class Command(BaseCommand):
    help = 'Import data from CSV files into the database using Pandas and bulk_create'

    def handle(self, *args, **kwargs):

        # Extract database settings from Django
        db_settings = settings.DATABASES['default']
        engine = create_engine(f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}")
        
        self.import_authors(engine)
        self.stdout.write(self.style.SUCCESS('Authors imported!'))
        self.import_publishers(engine)
        self.stdout.write(self.style.SUCCESS('Publishers imported!'))
        self.import_books(engine)
        self.stdout.write(self.style.SUCCESS('Books imported!'))
        self.import_users(engine)
        self.stdout.write(self.style.SUCCESS('Users imported!'))
        self.import_ratings(engine)
        self.stdout.write(self.style.SUCCESS('Ratings imported!'))

    def import_authors(self, engine):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'authors.csv'))
        df.to_sql('myproject_author', con=engine, if_exists='append', index=False)

    def import_publishers(self, engine):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'publishers.csv'))
        df.to_sql('myproject_publisher', con=engine, if_exists='append', index=False)

    def import_books(self, engine):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'books.csv'))
        df.to_sql('myproject_book', con=engine, if_exists='append', index=False)

    def import_users(self, engine):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'users.csv'))
        df.to_sql('myproject_user', con=engine, if_exists='append', index=False)

    def import_ratings(self, engine):
        df = pd.read_csv(os.path.join('myproject', 'data', 'postprocess', 'ratings.csv'))
        df.to_sql('myproject_ratings', con=engine, if_exists='append', index=False)
