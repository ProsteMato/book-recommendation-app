# import
import pandas as pd
import numpy as np # Review: Unnecessary import pandas can do exacly the same thing


# load ratings
ratings = pd.read_csv('Downloads/BX-Book-Ratings.csv', encoding='cp1251', sep=';')
ratings = ratings[ratings['Book-Rating']!=0] # Review:  Is good to removing 0, but should by at least commented why.

# load books
# Review:  error_bad_lines=False is depricated should use on_bad_lines=skip instead
# Review:  also consider using try except block
books = pd.read_csv('Downloads/BX-Books.csv',  encoding='cp1251', sep=';',error_bad_lines=False)

#users_ratigs = pd.merge(ratings, users, on=['User-ID']) # Review: this could be removed
dataset = pd.merge(ratings, books, on=['ISBN'])
dataset_lowercase=dataset.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)

tolkien_readers = dataset_lowercase['User-ID'][(dataset_lowercase['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1)') & (dataset_lowercase['Book-Author'].str.contains("tolkien"))]
# Review:  here you could use use tolkien_readers.unique() instead and remove the dependency on numpy
tolkien_readers = tolkien_readers.tolist()
tolkien_readers = np.unique(tolkien_readers)

# final dataset
books_of_tolkien_readers = dataset_lowercase[(dataset_lowercase['User-ID'].isin(tolkien_readers))]

# Number of ratings per other books in dataset
number_of_rating_per_book = books_of_tolkien_readers.groupby(['Book-Title']).agg('count').reset_index()

#select only books which have actually higher number of ratings than threshold
books_to_compare = number_of_rating_per_book['Book-Title'][number_of_rating_per_book['User-ID'] >= 8]
books_to_compare = books_to_compare.tolist()
# Review:  The threshold of 8 is hard-coded consider defining this as a variable at the top for easier adjustments.

ratings_data_raw = books_of_tolkien_readers[['User-ID', 'Book-Rating', 'Book-Title']][books_of_tolkien_readers['Book-Title'].isin(books_to_compare)]

# group by User and Book and compute mean
ratings_data_raw_nodup = ratings_data_raw.groupby(['User-ID', 'Book-Title'])['Book-Rating'].mean()

# reset index to see User-ID in every row
ratings_data_raw_nodup = ratings_data_raw_nodup.to_frame().reset_index()

dataset_for_corr = ratings_data_raw_nodup.pivot(index='User-ID', columns='Book-Title', values='Book-Rating')

LoR_list = ['the fellowship of the ring (the lord of the rings, part 1)']

result_list = []
worst_list = []

# for each of the trilogy book compute:
for LoR_book in LoR_list:
    
    #Take out the Lord of the Rings selected book from correlation dataframe
    dataset_of_other_books = dataset_for_corr.copy(deep=False)
    dataset_of_other_books.drop([LoR_book], axis=1, inplace=True)
    # Review:  I dont see the reason to copy the DataFrame
      
    # empty lists
    book_titles = []
    correlations = []
    avgrating = []

    # corr computation
    for book_title in list(dataset_of_other_books.columns.values):
        book_titles.append(book_title)
        correlations.append(dataset_for_corr[LoR_book].corr(dataset_of_other_books[book_title]))
        tab=(ratings_data_raw[ratings_data_raw['Book-Title']==book_title].groupby(ratings_data_raw['Book-Title']).mean())
        avgrating.append(tab['Book-Rating'].min())
    # final dataframe of all correlation of each book
    # Review: this loop for correlation is very inefficient, it can be computed in a single vectorized operation
    # Review: grouping and calling mean repeatedly is also inefficient
       
    corr_fellowship = pd.DataFrame(list(zip(book_titles, correlations, avgrating)), columns=['book','corr','avg_rating'])
    corr_fellowship.head()
    # Review: it okey but could be done with one vectorized operation

    # top 10 books with highest corr
    result_list.append(corr_fellowship.sort_values('corr', ascending = False).head(10))
    
    #worst 10 books
    worst_list.append(corr_fellowship.sort_values('corr', ascending = False).tail(10))
    
print("Correlation for book:", LoR_list[0])
#print("Average rating of LOR:", ratings_data_raw[ratings_data_raw['Book-Title']=='the fellowship of the ring (the lord of the rings, part 1'].groupby(ratings_data_raw['Book-Title']).mean()))
rslt = result_list[0]