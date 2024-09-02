from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from myproject.models import Book, Rating
from django.db.models import F, Avg, Value
from django.db.models.functions import Lower, Round
import pandas as pd

def search_page(request):
    return render(request, 'search.html')

def autocomplete(request):
    query = request.GET.get('query', '')
    if query:
        books = Book.objects.filter(title__icontains=query)[:5]
        results = [{'id': book.id, 'title': book.title} for book in books]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

def search_books(request):
    query = request.GET.get('query', '')
    if not query:
        return HttpResponse("No query provided.")
    
    books_with_ratings = Rating.objects.select_related('book', 'book__author').annotate(
        lower_title=Lower('book__title')
    ).values(
        'lower_title',
        'book_rating',
        'user__id'
    )
    
    dataset_lowercase = pd.DataFrame(list(books_with_ratings))
    
    book_readers = dataset_lowercase['user__id'][
        (dataset_lowercase['lower_title'] == query.lower())].unique()
    
    users_book = dataset_lowercase[(dataset_lowercase['user__id'].isin(book_readers))]
    
    number_of_rating_per_book = users_book.groupby(['lower_title']).agg('count').reset_index()
    
    books_to_compare = number_of_rating_per_book['lower_title'][number_of_rating_per_book['user__id'] >= 8]
    
    ratings_data_raw = users_book[['user__id', 'book_rating', 'lower_title']][users_book['lower_title'].isin(books_to_compare)]
    
    ratings_data_raw_nodup = ratings_data_raw.groupby(['user__id', 'lower_title'])['book_rating'].mean().reset_index()
    
    dataset_for_corr = ratings_data_raw_nodup.pivot(index='user__id', columns='lower_title', values='book_rating')
    
    correlations = dataset_for_corr.corrwith(dataset_for_corr[query.lower()])

    correlations = correlations.drop(index=query.lower())

    avg_ratings = ratings_data_raw.groupby('lower_title')['book_rating'].mean()

    correlations_data = pd.DataFrame({
        'Book': correlations.index,
        'Correlation': correlations.values,
        'Avg_Rating': correlations.index.map(avg_ratings)
    })

    # Drop any NaN correlations if they exist (optional)
    correlations_data.dropna(subset=['Correlation'], inplace=True)
    book_correlations_data = pd.DataFrame(correlations_data.sort_values('Correlation', ascending=False).head(10)).reset_index()["Book"].tolist()
    
    books = []
    
    if (len(book_correlations_data) > 1):
        for book_title in book_correlations_data:
            books.append(Book.objects.annotate(
                lower_title=Lower('title'),
                avg_rating=Round(Avg('rating__book_rating'), 2)
            ).filter(
                lower_title__icontains=book_title
            ).values("title", "author__name", "avg_rating", "image_url_l").first())
    
    return render(request, 'search_results.html', {'books': books})
