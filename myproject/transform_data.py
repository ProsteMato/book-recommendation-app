import pandas as pd
import numpy as np
from io import StringIO
import re
from rapidfuzz import fuzz
from tqdm import tqdm
import os

def standardize(name):
    name = re.sub(r'\.(\S)', r'. \1', name)
    name = re.sub(r'\b([A-Z])\b', r'\1.', name)
    name = re.sub(r'\.\.+', r'.', name)
    name = re.sub(r'\s+', ' ', name)
    return name.title().strip()

def standardize_title(title):
    while re.search(r'\([^()]*\)', title):
        title = re.sub(r'\([^()]*\)', '', title)
    title = title.strip()
    title = re.sub(r'\s+', ' ', title)
    
    return title

def load_data():
    df_ratings = pd.read_csv('./data/dataset/Ratings.csv', encoding='cp1251', sep=',', on_bad_lines='warn')
    
    users = pd.read_csv('./data/dataset/Users.csv', encoding='cp1251', sep=',', on_bad_lines='warn')
    
    with open('./data/dataset/Books.csv', 'r', encoding='cp1251') as file:
        decoded_content = file.read().replace('\\"";', '",').replace(",\n", "\n")

    books = pd.read_csv(StringIO(decoded_content), encoding='cp1251', sep=',', on_bad_lines='warn', dtype={
        "ISBN": object,
        "Book-Title": object,
        "Book-Author": object,
        "Year-Of-Publication": np.uint,
        "Publisher": object,
        "Image-URL-S": object,
        "Image-URL-M": object,
        "Image-URL-L": object,
    })
    
    return df_ratings, users, books

def transform_users(users):
    location_split = users['Location'].str.split(',', n=2, expand=True)

    users['city'] = location_split[0].str.strip()
    users['state'] = location_split[1].str.strip()
    users['country'] = location_split[2].str.strip()

    users['country'] = users['country'].str.upper()

    median_age = users['Age'].median()
    users['Age'] = users['Age'].fillna(median_age)

    users['Age'] = users['Age'].clip(lower=10, upper=100)

    users.drop(columns=['Location'], inplace=True)
    return users

def transform_ratings(ratings):
    return ratings[ratings["Book-Rating"] != 0]
    

def group_similar_authors_with_combined_fuzzy(name_list, threshold=95):
    processed_authors = [name.lower().strip() for name in name_list]
    
    groups = []
    seen = set()
    
    for i, author in tqdm(list(enumerate(processed_authors))):
        if author in seen:
            continue
            
        group = [author]
        seen.add(author)
        
        for j in range(i + 1, len(processed_authors)):
            if processed_authors[j] not in seen:
                similarity = max(
                    fuzz.ratio(author, processed_authors[j]),
                    fuzz.partial_ratio(author, processed_authors[j]),
                    fuzz.token_sort_ratio(author, processed_authors[j])
                )
                if similarity >= threshold:
                    group.append(processed_authors[j])
                    seen.add(processed_authors[j])
        
        groups.append(group)
    
    return [lst for lst in groups if len(lst) > 1]


def map_standardize(df, groups, column):
    author_mapping = {}
    for group in groups:
        primary_name = max(group, key=len)
        for name in group:
            author_mapping[standardize(name)] = standardize(primary_name)

    df[column] = df[column].replace(author_mapping)

def transform_books_and_ratings(books, ratings):
    books = books.dropna()
    
    book_rating_counts = ratings['ISBN'].value_counts()
    books_filtered = books[books['ISBN'].isin(book_rating_counts[book_rating_counts >= 1].index)]
    
    dataset = pd.merge(ratings, books_filtered, on=['ISBN'])
    dataset_lowercase = dataset.select_dtypes(include='object').apply(lambda x: x.str.lower())
    
    book_rating_counts_by_title = dataset_lowercase['Book-Title'].value_counts()
    books_filtered = books_filtered[books_filtered['Book-Title'].str.lower().isin(book_rating_counts_by_title[book_rating_counts_by_title >= 8].index)]
    
    ratings = ratings[ratings['ISBN'].isin(books_filtered['ISBN'])]
    
    books_filtered['Book-Author'] = books_filtered['Book-Author'].apply(standardize)
    books_filtered['Publisher'] = books_filtered['Publisher'].apply(standardize)
    books_filtered['Book-Title'] = books_filtered['Book-Title'].apply(standardize_title)
    
    authors_groups = group_similar_authors_with_combined_fuzzy(books_filtered['Book-Author'].unique())
    publisher_groups = group_similar_authors_with_combined_fuzzy(books_filtered['Publisher'].unique())
    
    map_standardize(books_filtered, authors_groups, "Book-Author")
    map_standardize(books_filtered, publisher_groups, "Publisher")
    
    return books_filtered, ratings
    
def create_author_and_publisher_df(books):
    authors = pd.DataFrame(books['Book-Author'].unique(), columns=['name'])
    authors['id'] = authors.index + 1

    publishers = pd.DataFrame(books['Publisher'].unique(), columns=['name'])
    publishers['id'] = publishers.index + 1

    author_id_map = pd.Series(authors['id'].values, index=authors['name']).to_dict()
    books['author_id'] = books['Book-Author'].map(author_id_map)

    publisher_id_map = pd.Series(publishers['id'].values, index=publishers['name']).to_dict()
    books['publisher_id'] = books['Publisher'].map(publisher_id_map)

    books = books.drop(columns=['Book-Author', 'Publisher'])
    return books, authors, publishers
    
def main():
    print("Loading data")
    ratings, users, books = load_data()
    print("Transforming ratings")
    ratings = transform_ratings(ratings)
    print("Transforming users")
    users = transform_users(users)
    print("Transforming books and ratings")
    books, ratings = transform_books_and_ratings(books, ratings)
    print("Creating authors and publishers dataframe")
    books, authors, publishers = create_author_and_publisher_df(books)
    
    print("Renaming")
    
    books.reset_index(drop=True, inplace=True)
    books['id'] = books.index + 1
    
    ratings = ratings.merge(books[["id", "ISBN"]], on="ISBN", how="left").drop(columns=["ISBN"])
    
    ratings = ratings.rename(columns={
        "User-ID": "user_id",
        "Book-Rating": "book_rating",
        "id": "book_id"
    })
    
    books = books.rename(columns={
        "ISBN": "isbn",
        "Book-Title": "title",
        "Year-Of-Publication": "year_of_publication",
        "Image-URL-S": "image_url_s",
        "Image-URL-M": "image_url_m",
        "Image-URL-L": "image_url_l",
    })
    
    users = users.rename(columns={
        "User-ID": "id",
        "Age": "age"
    })
    
    users.reset_index(drop=True, inplace=True)
    ratings.reset_index(drop=True, inplace=True)
    
    users['id'] = users.index + 1
    ratings['id'] = ratings.index + 1
    
    print("Storing to csv files")
    ratings.to_csv("data/postprocess/ratings.csv", index=False)
    books.to_csv("data/postprocess/books.csv", index=False)
    users.to_csv("data/postprocess/users.csv", index=False)
    authors.to_csv("data/postprocess/authors.csv", index=False)
    publishers.to_csv("data/postprocess/publishers.csv", index=False)
    

if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    main()
    
    