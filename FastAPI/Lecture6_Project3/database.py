from sqlalchemy import create_engine # This import is necessary to create a SQLAlchemy engine, which manages connections to the database.
from sqlalchemy.orm import sessionmaker # This import is necessary to create a session factory, which will generate session objects for interacting with the database.
from sqlalchemy.ext.declarative import declarative_base # This import is necessary to create a base class for our ORM models.

# This line is saying that we are using SQLite as our database and the database file will be named 'todos.db' located in the current directory.
SQLAlchemy_DATABASE_URL = 'sqlite:///./todos.db' 

'''Now we need to make an engine.
 This line is saying that we are creating a SQLAlchemy engine that will manage connections to our SQLite database.
 The connect_args={'check_same_thread': False} part is specific to SQLite. It allows the same connection to be used across different threads, 
 which is necessary for FastAPI's asynchronous environment.
 '''
engine = create_engine(SQLAlchemy_DATABASE_URL, connect_args={'check_same_thread': False})

''' 
The following line creates a session factory, which will be used to generate new session objects for interacting with the database.
Autocommit is a setting that determines whether each individual statement is automatically committed to the database. 
When autocommit is set to False, changes are not saved until explicitly committed.

Autoflush is another setting that determines whether changes made to the session are automatically flushed to the database before 
certain operations, such as queries. 

bind: This specifies the engine to which the session will be bound. In this case, it is the engine we created for our SQLite database.
'''
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # This creates a base class for our ORM models. All ORM models will inherit from this base class.

