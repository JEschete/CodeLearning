"""
Books Project Introduction: 
What will we be creating. 
Creating and enhancing books to lear the basics of FastAPI. 

We will have a list of books in a key value pair. 

We will use the CRUD operations. 
C - Create - Add a new book to the list
R - Read - Retrieve information about a book
U - Update - Modify details of an existing book
D - Delete - Remove a book from the list

Request and Response
We will  have a webpage, it will send a request, and the server will respond. 
It's going to use HTTP request methods. 

FastAPI has swagger UI. 

HTTP Request methods have their own verbs attached to the CRUD operations. 
CRUD    HTTP Request Method
Create  POST
Read    GET
Update  PUT
Delete  DELETE

The first thing covered will be to create a get request method so we can read and 
return information back to the client who is requesting information from FASTAPI.

we first do the import of FastAPI, then we create an instance of the FastAPI class.
Then we do:

app = FastAPI() # This creates an instance of the FastAPI class and assigns it to the variable app. 

This instance will be used to define routes and handle incoming requests.

The we create our:
@app.get("/api-endpoint") # This is a decorator that defines a route for the GET request method.
The route is specified as "/api-endpoint", which means that when a client sends a GET request to this URL, the associated function will be executed.
async def first_api(): 
    return {"message": "Hello, World!"} # This is the function that will be executed when a GET request is made to the specified route. 
    
It returns a JSON response with a message.

async is not needed in FastAPI, we are being explicit about the fact that this function is asynchronous.
We need to add an API endpoint as shown above.


How to start the FastAPI application? 
We will use the terminal to run the FastAPI application using the command:
uvicorn Books:app --reload

uvicorn is the server, books is the name of the file, app is the instance of the FastAPI class, 
and --reload is an option that enables automatic reloading of the application when code changes are detected.

We will change the above to be: 
@app.get("/books")
async def read_all_books():
    return BOOKS

We haven't defined the BOOKS variable yet, but we will do that next.

We do want to select the right interpreter. In VS Code, we can select the interpreter by clicking on the Python version in the bottom left corner of the window.
Then we can select the interpreter that we want to use.
"""

"""
Path paramaters
What are path parameters?
Path parameters are request parameters that have been attached to the URL. 
Path parameters are usually defined as a way to find information based on location. 
Think of a computer file system. 
- You can identify the specific resources based on the file you are in. 

Path Parameters
Say we have 
REQUEST: 
URL: 127.0.0.1:8000/books

That is a static path. 
You can in fastAPI make dynamic paths. 

So:
REQUEST:
URL: 127.0.0.1:8000/books/book_one. 

# note the api endpoint dynamic param in the curly braces needs to match the parameter name in the function definition.
@app.get("/books/{dynamic_param}")
async def read_all_books(dynamic_param):
    return {'dynamic_param': dynamic_param}

RESPONSE: 
{
    "dynamic_param": "book_one"
}

With path parameters, order matters. Smaller api endpoints should be defined before larger api endpoints.
For example, if we have the following two endpoints:
@app.get("/books/{book_id}")
@app.get("/books/{book_id}/reviews")

The first endpoint will match any request that starts with "/books/" and has a single path parameter.
The second endpoint will match any request that starts with "/books/" and has two path parameters.

Request: 
URL: 127.0.0.1/books/title%20four # %20 is a space in the URL.

@app.get("/books/{book_title}")
async def read_book_by_title(book_title: str):
    for book in BOOKS:
        if book['title'] == book_title:
            return book

"""


"""
Query Parameters
What are query parameters?

Query Parameters are request parameters that are attached to the URL after a question mark (?).
Query Paramters have a name=value pair.

They allow us to filter data based on the URL. 

For example, if we have the following URL:
127.0.0.1:/books/?category=math

So if we have the request:
URL:127.0.0.1:/books/?category=science

we would have:
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    
    return books_to_return

Query paramters can be used with path parameters.
so if we have:
URL:127.0.0.1:/books/author%20four/?category=math


"""


"""
POST HTTP Request Method
What is the POST Request Method
- Used to create data
- can have a body that has additional information that GET does not have
- Example:
    {"title":"Title Seven", "author":"Author Two", "category":"math"}

POST Request Method
Request
URL: 127.0.0.1:8000/books/create_book
@app.post("/books/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)



"""