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
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.dict())
    BOOKS.append(new_book)