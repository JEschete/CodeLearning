from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Todos(Base):
    __tablename__='todos' # Says what to name the table. 

    ''' 
    The following line defines the primary key column for the table.
    The column method defines a column in the table.
    In this case, it defines an integer column named 'id' which is the primary key and indexed.

    A primary key is a unique identifier for each record in the table.
    The index=True argument creates an index on this column, which can improve query performance by allowing faster lookups.
    '''
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False) # In a Databse, 0 = False, 1 = True

