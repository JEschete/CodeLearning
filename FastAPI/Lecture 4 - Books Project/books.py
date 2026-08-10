"""Creating a FastAPI app for learning CRUD and routing basics."""

from fastapi import Body, FastAPI

app = FastAPI()

# In-memory sample data used for learning. This resets whenever the server restarts.
BOOKS: list[dict[str, str]] = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'Science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'Science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'History'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'Math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'Math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'Math'}
]


def _find_book_index_by_title(title: str) -> int:
    """Return the index of the first matching title, or -1 when no match exists."""
    # casefold() is used for case-insensitive matching across all title lookups.
    for i, book in enumerate(BOOKS):
        if book.get('title').casefold() == title.casefold():
            return i
    return -1


# Basic read endpoint that returns every book.
@app.get("/books")
async def read_all_books():
    return BOOKS


# Use explicit path segments to avoid collisions between dynamic routes.
@app.get("/books/title/{book_title}")
async def read_book_by_title(book_title: str):
    # Reuse helper logic so all title-based lookups behave the same way.
    book_index = _find_book_index_by_title(book_title)
    if book_index == -1:
        # Keep the response simple for now; we can introduce exceptions later.
        return {"message": "Book not found"}
    return BOOKS[book_index]


# Path-parameter version: author is supplied in the URL path.
@app.get("/books/by-author/{author}")
async def read_books_by_author_path(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return


# Query-parameter version: author is supplied as ?author=...
@app.get("/books/by-author")
async def read_books_by_author_query(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return


# Category filter endpoint using query parameters.
@app.get("/books/by-category")
async def read_books_by_category_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# Combined filter: author is a path parameter, category is a query parameter.
@app.get("/books/by-author/{book_author}/by-category")
async def read_books_by_author_and_category(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


# Create endpoint. Body() reads JSON request data into new_book.
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    return new_book


# Update endpoint. Expects a full replacement book object in the body.
@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    # Empty string fallback avoids attribute errors if title is missing.
    book_index = _find_book_index_by_title(updated_book.get('title', ''))
    if book_index == -1:
        return {"message": "Book not found"}
    BOOKS[book_index] = updated_book
    return {"message": "Book updated successfully", "book": updated_book}


# Delete endpoint removes one matching book by title.
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    book_index = _find_book_index_by_title(book_title)
    if book_index == -1:
        return {"message": "Book not found"}
    deleted_book = BOOKS.pop(book_index)
    return {"message": "Book deleted successfully", "book": deleted_book}