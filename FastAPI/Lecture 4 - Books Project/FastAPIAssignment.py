from fastapi import Body, FastAPI

"""
Assignment

Here is your opportunity to keep learning!

1. Create a new API Endpoint that can fetch all books from a specific author using either Path Parameters or Query Parameters.

"""

# Initially I tried to import the books.py and use its stuff, but the below did not work because of route collisions. 
# I need to remember to order things most specific to most broad. 

app = FastAPI()

BOOKS: list[dict[str, str]] = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'Science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'Science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'History'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'Math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'Math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'Math'}        
]


# Initiallly this only return the first book found because it did not build a list. 
@app.get("/books/{author}")
async def read_book_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return

@app.get("/books/")
async def read_book_by_author_query(author: str):
    books_to_return = []
    for book in BOOKS: 
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)

    return books_to_return