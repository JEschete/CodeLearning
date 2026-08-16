"""
Books Project Introduction

Project goal:
Create and enhance a small Books API while learning the basics of FastAPI.

The project stores books in a Python list named BOOKS. Each item in the list is a dictionary, and
each dictionary stores one book as key-value pairs:

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'Science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'History'}
]

This is in-memory data. Changes disappear when the application restarts because the books are not
stored in a database yet.

CRUD Operations
C - Create: Add a new book.
R - Read: Retrieve one or more books.
U - Update: Replace or modify an existing book.
D - Delete: Remove a book.

CRUD operations commonly map to these HTTP request methods:

CRUD Operation    HTTP Method
Create            POST
Read              GET
Update            PUT or PATCH
Delete            DELETE

HTTP Requests and Responses
A client, such as a browser, mobile application, or Swagger UI, sends an HTTP request to the API.
FastAPI processes the request and sends an HTTP response back to the client.

A request can contain:
- A method, such as GET, POST, PUT, PATCH, or DELETE.
- A path, such as /books.
- Path or query parameters used to identify or filter data.
- A request body, usually JSON, used to send data to the API.

A response can contain:
- An HTTP status code, such as 200 OK or 404 Not Found.
- A response body containing JSON data.
- Response headers containing additional information.

Creating the FastAPI Application
First, import FastAPI and create an application instance:

from fastapi import FastAPI

app = FastAPI()

The app variable represents the FastAPI application. Uvicorn uses this object to start the API,
and decorators such as @app.get connect URL paths to Python functions.

GET HTTP Request Method
GET is used to read data without changing it.

@app.get("/api-endpoint")
async def first_api():
    return {"message": "Hello, World!"}

How this endpoint works:
1. @app.get registers a route that accepts GET requests.
2. "/api-endpoint" is the URL path for the route.
3. FastAPI calls first_api when a GET request matches that method and path.
4. The returned Python dictionary is serialized into a JSON response.

FastAPI supports route functions written with either async def or def. Use async def when the
function needs to await asynchronous work. A normal def is appropriate for synchronous work.

The Books endpoint returns the entire list:

@app.get("/books")
async def read_all_books():
    return BOOKS

FastAPI Documentation
FastAPI automatically creates interactive API documentation:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Swagger UI lists the available endpoints, their parameters, and their response schemas. The
"Try it out" button can send requests directly to the running API.

Starting the Application
1. Select the intended Python interpreter in VS Code with the Python: Select Interpreter command.
2. Open a terminal in the folder containing books.py.
3. Start the development server:

uvicorn books:app --reload

Command breakdown:
- uvicorn starts the ASGI development server.
- books is the Python module name from books.py.
- app is the FastAPI instance created by app = FastAPI().
- --reload restarts the server when source files change and is intended for development.
"""

"""
Path Parameters
What is a path parameter?

A path parameter is a variable value inside the URL path. It is commonly used to identify one
specific resource.

Static path:
http://127.0.0.1:8000/books

Dynamic path:
http://127.0.0.1:8000/books/title/Title%20Four

In the dynamic URL, "Title%20Four" is the path parameter value. %20 is the URL-encoded form of a
space.

Path parameters are declared with braces in the route:

@app.get("/books/title/{book_title}")
async def read_book_by_title(book_title: str):
    ...

How this endpoint works:
1. {book_title} marks that segment of the path as dynamic.
2. The name inside the braces must match the function parameter name book_title.
3. FastAPI takes the value from the URL and passes it to the function.
4. The str annotation tells FastAPI that the value should be treated as a string.
5. The loop compares the requested title with each book title.
6. casefold() makes the comparison case-insensitive.

Example request:
METHOD: GET
URL: http://127.0.0.1:8000/books/title/Title%20Four

Example response:
{
    "title": "Title Four",
    "author": "Author Four",
    "category": "Math"
}

Route Order
FastAPI checks routes in the order they are registered. Order matters when a static route and a
dynamic route could both match the same method and URL shape.

Define the static route first:

@app.get("/books/mybook")
async def read_favorite_book():
    return {"book_title": "My favorite book!"}

@app.get("/books/{book_title}")
async def read_book_by_title(book_title: str):
    return {"book_title": book_title}

If the dynamic route came first, the request /books/mybook could treat "mybook" as book_title.
Routes with different path shapes, such as /books/{book_id} and /books/{book_id}/reviews, do not
have this specific conflict because they contain different numbers of path segments.

Why this matters in this project:
Using explicit path segments, such as /books/title/{book_title} and /books/by-author/{author},
avoids ambiguous route patterns and reduces accidental collisions.

If no book matches, this learning example reaches the end of the function and returns null with a
200 response. A production API should normally return a 404 Not Found response instead.
"""


"""
Query Parameters
What is a query parameter?

A query parameter is a named value added to the URL after a question mark (?). Query parameters
are commonly used to filter, sort, search, or paginate a collection.

Query parameter format:
http://127.0.0.1:8000/books/by-category?category=Science

The query parameter above has:
- Name: category
- Value: Science

Multiple query parameters are separated with an ampersand:
/books/by-category?category=Science&sort=title

In FastAPI, a function parameter that is not part of the route path is interpreted as a query
parameter:

@app.get("/books/by-category")
async def read_books_by_category_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return

Example request:
METHOD: GET
URL: http://127.0.0.1:8000/books/by-category?category=Science

FastAPI passes "Science" to the category parameter. The endpoint returns every book whose category
matches, or an empty list if no books match.

Because category has no default value, it is required. Calling /books/by-category without category causes
FastAPI to return a 422 validation response. A query parameter can be made optional by giving it a
default value, for example category: str | None = None.

Author query endpoint example:

@app.get("/books/by-author")
async def read_books_by_author_query(author: str):
    ...

Example request:
METHOD: GET
URL: http://127.0.0.1:8000/books/by-author?author=Author%20Two

Combining Path and Query Parameters
A route can use both kinds of parameters in the same request:

@app.get("/books/by-author/{book_author}/by-category")
async def read_books_by_author_and_category(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
                book.get('category').casefold() == category.casefold():
            books_to_return.append(book)

    return books_to_return

Example request:
METHOD: GET
URL: http://127.0.0.1:8000/books/by-author/Author%20Two/by-category?category=Math

In this request:
- Author Two is the book_author path parameter.
- Math is the category query parameter.

GET requests should generally use path and query parameters rather than a request body.
"""


"""
POST HTTP Request Method
What is the POST Request Method?

POST is used to create a new resource. In this project, the request sends a new book as JSON and
the endpoint appends it to the BOOKS list.

Unlike a typical GET request, POST normally includes a request body. The body contains data sent by
the client rather than data encoded into the URL.

Example request:
METHOD: POST
URL: http://127.0.0.1:8000/books/create_book
BODY:
{
    "title": "Title Seven",
    "author": "Author Two",
    "category": "Math"
}

The Body class must be imported from FastAPI:

from fastapi import Body

@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    return new_book

How this endpoint works:
1. @app.post registers an endpoint that accepts POST requests.
2. Body() tells FastAPI to read the JSON request body.
3. FastAPI converts the JSON object into a Python dictionary named new_book.
4. BOOKS.append(new_book) adds the dictionary to the in-memory list.
5. Returning new_book sends the created book back to the client as JSON.

POST is generally not idempotent. Sending the same request twice runs append twice and creates two
list entries unless the API adds duplicate checking.

Common POST responses:
- 201 Created: The resource was created successfully.
- 400 Bad Request: The supplied request was not acceptable.
- 422 Unprocessable Entity: FastAPI could not validate the request data.

This example accepts any JSON value because Body() has no schema. In a larger application, a
Pydantic model should define required fields and types. The new book also exists only in memory, so
it disappears when the server restarts.
"""

"""
PUT HTTP Request Method
What is the PUT Request Method?
- PUT is used to update an existing resource.
- In CRUD, PUT represents the Update operation.
- A PUT request usually contains a request body with the new version of the resource.
- PUT normally replaces the entire resource. If we only want to change some fields, PATCH is
  generally the more appropriate HTTP method.

PUT is different from POST:
- POST creates a new resource and can add another item to the BOOKS list.
- PUT finds an existing resource and replaces it with the information in the request body.

PUT requests are intended to be idempotent. This means that sending the same PUT request more
than once should leave the server in the same final state. It should not create duplicate books.

PUT Request Method
Request:
METHOD: PUT
URL: http://127.0.0.1:8000/books/update_book
BODY:
{
    "title": "Title One",
    "author": "Updated Author",
    "category": "Updated Category"
}

The body contains the complete book that should replace the existing book. In this project, the
title is used to find the book that needs to be updated.

@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    book_index = _find_book_index_by_title(updated_book.get('title', ''))
    if book_index == -1:
        return {"message": "Book not found"}
    BOOKS[book_index] = updated_book
    return {"message": "Book updated successfully", "book": updated_book}

How this endpoint works:
1. @app.put defines an endpoint that accepts HTTP PUT requests.
2. Body() tells FastAPI to read the JSON request body and assign it to updated_book.
3. A helper function finds the matching index by title so update and delete can share logic.
4. The title from each existing book is compared with the title from the request body.
5. casefold() makes the title comparison case-insensitive.
6. When the titles match, BOOKS[book_index] = updated_book replaces the old dictionary with the
   new dictionary.
7. If no match is found, the endpoint returns a "Book not found" message.
8. On success, the endpoint returns a confirmation message and the updated book.

Because PUT replaces the complete book dictionary, the request body should include every field we
want the book to keep. For example, if category is omitted, the replacement dictionary will no
longer contain a category. A partial update would normally use PATCH instead.

Using the title as the identifier is fine for this learning project, but real applications commonly
use a unique, stable ID in the URL, such as PUT /books/3. A stable ID allows a title to be changed
without losing the ability to find the original book.

Common PUT responses:
- 200 OK: The resource was updated and a response body was returned.
- 204 No Content: The resource was updated and no response body was returned.
- 404 Not Found: No resource matched the supplied identifier.
- 422 Unprocessable Entity: FastAPI could not validate the supplied request data.

This project version keeps not-found handling simple by returning a message. Later, after exception
handling is introduced, this can be upgraded to return explicit HTTP error status codes. A Pydantic
model can also be used instead of an untyped Body() value to validate the book fields.

"""

"""
Delete HTTP Request Method
What is the DELETE request method?

DELETE is used to remove an existing resource. In this project, it removes one book from the
BOOKS list by matching the title in the path parameter.

Example request:
METHOD: DELETE
URL: http://127.0.0.1:8000/books/delete_book/Title%20One

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    book_index = _find_book_index_by_title(book_title)
    if book_index == -1:
        return {"message": "Book not found"}
    deleted_book = BOOKS.pop(book_index)
    return {"message": "Book deleted successfully", "book": deleted_book}

How this endpoint works:
1. @app.delete registers a route for HTTP DELETE requests.
2. {book_title} in the URL becomes the book_title function parameter.
3. A helper function checks each title in BOOKS and returns the matching index.
4. casefold() enables case-insensitive matching.
5. BOOKS.pop(book_index) removes the matching entry from the list.
6. The endpoint returns a success message and the deleted book.

Why this matters:
- Returning a clear success message helps clients confirm exactly what changed.
- Returning a clear not-found message keeps behavior understandable before exceptions are taught.
- This project now uses explicit not-found handling for delete and update.

Common DELETE responses:
- 200 OK: Deletion succeeded and a response body is returned.
- 204 No Content: Deletion succeeded and no body is returned.
- 404 Not Found: The resource to delete does not exist.

Route consistency note:
Keep path style consistent across your API. Using explicit endpoint names, such as /books/by-author
and /books/by-category, makes route intent clear and avoids accidental collisions.
"""