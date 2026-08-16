from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from starlette import status # starlette is used for HTTP status codes

# Path lets us validate and enforce constraints on path parameters.

app = FastAPI()

# Book is the application's in-memory object. Incoming API data is validated
# separately by BookRequest before it is converted into a Book.
class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

# Pydantic checks incoming JSON against these types and Field constraints before
# FastAPI calls an endpoint that accepts a BookRequest.
class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=-1, lt=6)
    published_date: int = Field(gt=-3000, lt=2500)

    # In Pydantic v2, model_config replaces the nested Config class used in v1.
    # json_schema_extra adds this example request body to FastAPI's generated docs.
    model_config = {
        "json_schema_extra" : {
            "example" : {
                "title" : "A new book",
                "author" : "CodingWithRoby",
                "description":"A good book",
                "rating": 5,
                "published_date": 2012

            }
        }
    }

# This list acts as an in-memory data store, so its changes disappear whenever
# the application restarts.
BOOKS = [
    Book(1, "Computer Science Pro", "CodingWithRoby", "A very nice book!", 5, 2005),
    Book(2, "Be Fast with FastAPI", "CodingWithRoby", "A great book!", 5, 2006),
    Book(3, "Master Endpoints", "CodingWithRoby", "A awesome book!", 5, 2005),
    Book(4, "HP1", "Author 1", "Book Description", 2, 2005),
    Book(5, "HP2", "Author 2", "Book Description", 3, 1999),
    Book(6, "HP3", "Author 3", "Book Description", 1, 2020),
]


@app.get("/books", status_code=status.HTTP_200_OK) # this is not a great api boundary because later we use /books/ and the lack of trailing slash can cause ambiguity
async def read_all_books():
    return BOOKS

# This earlier approach accepts an untyped request body. Without a Pydantic
# model, FastAPI cannot enforce required fields, data types, or Field constraints.
# @app.post("/create-book")
# async def create_book(book_request=Body()):
#     BOOKS.append(book_request)

# The int annotation makes FastAPI parse and validate the path parameter before
# the endpoint runs.
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)): # We are now saying the book_id must be greater than 0. This helps ensure that invalid IDs like negative numbers are rejected before the endpoint logic runs.
    for book in BOOKS:
        if book.id == book_id:
            return book
    # if the user requests a book that does not exist we can raise a 404.
    raise HTTPException(status_code=404, detail='Item not found') 


        

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int=Query(gt=0, lt=6)): # Here we are showing that the query must fall within the parameters.  
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

# # For Assignment problem, original solution
# @app.get("/books/by_pub_date")
# async def read_book_by_pub_date(published_date: int):
#     books_to_return = []
#     for book in BOOKS:
#         if book.published_date == published_date:
#             books_to_return.append(book)
#     return books_to_return

# For Assignment problem, they did the following because the previous approach with "/books/by_pub_date" 
# was not ideal because it could conflict with other endpoints and was less intuitive than using a query 
# parameter with a more general path like "/books/publish/".
@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_book_by_pub_date(published_date: int=Query(gt=1999,lt=2050)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest): 
    # In Pydantic v2, model_dump() returns a dictionary; ** unpacks it into Book.
    new_book = Book(**book_request.model_dump())
    BOOKS.append(find_book_id(new_book))

# Assign IDs on the server instead of trusting client input, which could conflict
# with an existing book's ID.
def find_book_id(book: Book):
    # This conditional expression starts at 1 or increments the last stored ID.
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    # The caller appends this returned object; without return, it would append None.
    return book

    # The same ID assignment written as a standard if/else block:
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1

    # return book 

# Why below do we need to pass in an ID? 
# In our resquest in BookRequest, ID is optional. 
@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = Book(**book.model_dump()) # We had to add ** to unpack the dictionary returned by model_dump() into the Book constructor
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found. ')

# Delete book method. 
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int=Path(gt=0)): # Ensure the book_id is positive.
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break # Break is required because otherwise it will continue to loop and throw an error because the list is now shorter.
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found. ')