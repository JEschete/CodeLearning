Project 2
Project two will still focus on creating book api endpoints. 

Continued education includes: 
- GET, POST, PUT, DELETE request methods. 

New Information will include:
- Data validation, exception handling, status codes, swagger configuration, and python request objects. 

Creating a new books project
- We will create a new class called book
- We will be using these books throughout the project. 

On top of data validations we are going to reenforce the CRUD HTTP Request Methods. 
CRUD        HTTP
Create      POST
Read        GET
Update      PUT
Delete      DELETE

Pydantic Notes:
Pydantic v1 vs Pydantic v2
FastAPI is now compatible with both Pydantic v1 and Pydantic v2.

Based on how new the version of FastAPI you are using, there could be small method name changes.

The three biggest are:

.dict() function is now renamed to .model_dump()

schema_extra function within a Config class is now renamed to json_schema_extra

Optional variables need a =None example: id: Optional[int] = None

At some point we want to have some type of validation. 

----------------------------------------------------------
Pydantics
What is pydantics? 

- A Python library that is used for data modeling, data parsing, and has efficient error handling. 
- Pydantics is commonly used as a resource for data validation and how to handle data coming to our FastAPI application. 

We will be implementing pydantics
- Create a different request model for data validation. 
- Field data validation on each variable / element

# Inheriting from Basemodel gives us more functionality. 
class BookRequest(BaseModel):
    id: int
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=5)

BookRequest and Book Conversion
- We convert the pydantics request into a Book

@app.post("/create-book")
async def create_book(book_request: BookRequest): # We have to make the BookRequest 
    new_book = Book(**book_request.dict()) # **  operator will pas the key/value from BookRequest() into the Book() constructor. 
    BOOKS.append(new_book)

----------------------------------------------------------
FastAPI Project: Pydantic Configurations

----------------------------------------------------------
## FastAPI Path and Query Parameters

Parameters let an endpoint receive values from the URL. FastAPI determines
whether a function parameter is a path parameter or a query parameter by
comparing the function signature with the route path.

### URL anatomy

```text
Full URL:     http://127.0.0.1:8000/books/3?include_details=true
Path:         /books/3
Path value:   3
Query string: ?include_details=true
```

- `/books/3` is the URL path.
- `3` is a path parameter value.
- `?` starts the query string.
- `include_details=true` is a query parameter written as `name=value`.
- Multiple query parameters are separated with `&`, such as
    `?book_rating=5&author=CodingWithRoby`.

### Path parameters

A path parameter is part of the route itself. Place its name inside `{}` in
the decorator and use the same name in the function signature.

```python
@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book.id == book_id:
            return book
```

Example request:

```text
GET http://127.0.0.1:8000/books/3
```

FastAPI takes `3` from the URL and passes it to `read_book()` as `book_id`.
Path parameters normally identify one specific resource, such as a book, user,
or order.

Important path parameter concepts:

- The names must match: `{book_id}` maps to the `book_id` argument.
- A path parameter is required because the route cannot match without that
    path segment.
- The `int` annotation tells FastAPI to convert the URL text into an integer.
- `/books/abc` fails validation because `abc` cannot be converted to `int`.
- Type annotations also appear in the generated Swagger documentation.

The type check only proves that a value is a valid integer. For example,
`/books/999` passes type validation even if book 999 does not exist. Looking up
the book and returning `404 Not Found` is separate application logic.

Additional validation can be declared with FastAPI's `Path` helper:

```python
from fastapi import Path

@app.get("/books/{book_id}")
async def read_book(book_id: int = Path(gt=0)):
    ...
```

Here, `gt=0` means the ID must be greater than zero.

### Query parameters

A query parameter comes after `?` in the URL and is not included inside the
route path. If a simple function parameter is not named in the route path,
FastAPI treats it as a query parameter.

```python
@app.get("/books/")
async def read_book_by_rating(book_rating: int):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return
```

Example request from this project:

```text
GET http://127.0.0.1:8000/books/?book_rating=5
```

FastAPI reads the text after `book_rating=` and passes its converted integer
value to `read_book_by_rating()`. Query parameters commonly handle filtering,
searching, sorting, and pagination rather than identifying one resource.

Important query parameter concepts:

- The query parameter name normally matches the function argument name.
- `book_rating: int` is required because it has no default value.
- Omitting a required query parameter produces a `422` validation response
    before the endpoint function runs.
- `?book_rating=five` also produces `422` because `five` is not an integer.
- Raw URL values are text, but FastAPI converts and validates them using the
    function's type annotations.

### Required, default, and optional query parameters

A query parameter without a default is required:

```python
async def read_book_by_rating(book_rating: int):
```

A query parameter with a default can be omitted:

```python
async def read_books(book_rating: int = 5):
```

An optional query parameter can use `None` to mean "no filter supplied":

```python
async def read_books(book_rating: int | None = None):
    if book_rating is None:
        return BOOKS
```

With an optional filter, `/books` can return every book while
`/books?book_rating=5` can return only books rated 5.

The `Query` helper can add validation and documentation:

```python
from fastapi import Query

@app.get("/books/")
async def read_book_by_rating(book_rating: int = Query(ge=0, le=5, description="Filter by rating")): ...
```

- `ge=0` means greater than or equal to 0.
- `le=5` means less than or equal to 5.
- `description` appears in the generated API documentation.

### Path parameters versus query parameters

| Path parameter | Query parameter |
| --- | --- |
| Written inside the path, such as `/books/{book_id}` | Written after `?`, such as `/books?book_rating=5` |
| Usually identifies one resource | Usually filters or changes a collection |
| Required for the route to match | Can be required, optional, or have a default |
| Declared with `{name}` in the route decorator | Not written in the route decorator |
| Can use FastAPI's `Path` helper | Can use FastAPI's `Query` helper |

### How FastAPI classifies endpoint inputs

For an endpoint function parameter:

1. If its name appears inside `{}` in the route, it is a path parameter.
2. If it has a simple type such as `str`, `int`, `float`, or `bool` and is not
     in the route path, it is normally a query parameter.
3. If its type is a Pydantic model such as `BookRequest`, FastAPI reads it from
     the request body.

```python
@app.post("/books/{category}")
async def create_book(category: str, book: BookRequest, notify: bool = False): ...
```

- `category` is a path parameter because it appears in `{category}`.
- `book` is a request body because `BookRequest` is a Pydantic model.
- `notify` is a query parameter because it is a simple type that does not
    appear in the route path.

Example request:

```text
POST /books/programming?notify=true
```

### Routing details to remember

- FastAPI selects a route using the HTTP method and URL path. The query string
    is not used to choose between two endpoint functions.
- In the current project, `/books` maps to `read_all_books()`, while `/books/`
    maps to `read_book_by_rating()`. Therefore, the rating request includes the
    trailing slash: `/books/?book_rating=5`.
- `/books` and `/books/` are different paths. Production APIs normally choose
    one consistent trailing-slash style.
- Put fixed paths before dynamic paths when they could overlap. For example,
    define `/books/by-rating` before `/books/{book_id}`; otherwise `by-rating`
    may be interpreted as the value of `book_id`.
- Path and query values are visible in URLs and may appear in browser history or
    server logs, so sensitive values should not be placed in them.

Both parameter types can be tested interactively at:

```text
http://127.0.0.1:8000/docs
```
    



----------------------------------------------------------
We have no built in validation. 

What if a book doesn't exist and how do we ensure a book ID is positive. 
We can import Path from FastAPI and use it to enforce constraints on path parameters, such as ensuring a book ID is positive.

This will cause invalid book IDs, such as negative numbers or zero, to be rejected before the endpoint logic runs.
They will return a 422 Unprocessable Entity response, indicating that the provided path parameter does not meet the specified constraints.

