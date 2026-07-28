"""
Creating a FastAPI app
"""

from fastapi import Body, FastAPI

app = FastAPI() # This allows uvicorn to find the app instance when we run the command uvicorn Books:app --reload

BOOKS: list[dict[str, str]] = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'Science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'Science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'History'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'Math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'Math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'Math'}        
]


@app.get("/books") # This is a decorator that defines a route for the GET request method.
async def read_all_books(): # Async is not needed in FastAPI, we are being explicit about the fact that this function is asynchronous.
    return BOOKS # The printed response is not well formatted. 

# # Because order matters, we moved this function above the dynamic path function.
# @app.get("/books/mybook")
# async def read_all_books():
#     return {'book_title': 'My favorite book!'} # This is the function that will be executed when a GET request is made to the specified route.

@app.get("/books/{book_title}") # This is a decorator that defines a route for the GET request method.
async def read_books(book_title: str): # we can type def to enforce the type of the parameter. 
    for book in BOOKS: 
        if book.get('title').casefold() == book_title.casefold(): # casefold() is a method that returns a case-insensitive version of the string. 
            return book

# # Because order matters, if we try to execute the following code, instead of calling the below, it will call the above because it is a dynamic path.
# @app.get("/books/mybook")
# async def read_all_books():
#     return {'book_title': 'My favorite book!'} # This is the function that will be executed when a GET request is made to the specified route.

""" 
FastAPI has swagger UI. Which is a web interface that allows us to interact with the API endpoints. 
It provides a user-friendly way to test and explore the API.

If we "try it out" in the swagger UI, we can see the response from the API endpoint.
A response of 200 means that the request was successful and the server returned the requested data.

Swagger allows us to easily see all api's and test their functionality. 
It provides a convenient way to explore and interact with the API endpoints without the need for external tools or manual testing.
"""
@app.get("/books/") # Anything passed in after this, is a query.
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS: 
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return


@app.get("/books/{book_author}/") # Get requests do not have a body. 
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS: 
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return

@app.post("/books/create_book") # Post can have a body
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

