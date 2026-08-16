Project 3
----------------------
Project three will be switching our focus to TODOS instead of BOOKS
New Information will include: 
- Full SQL Database
    - SQLite
    - PostgresSQL
    - MySQL
- Authentication with JWT Tokens
- Authorization
- Hashing Passwords

Creating a Todo Table
- Create Todo Table Models for our application
- Use the Todos to save records throughout this project. 

Pydantic v1 vs Pydantic v2
FastAPI is now compatible with both Pydantic v1 and Pydantic v2.

Based on how new the version of FastAPI you are using, there could be small method name changes.

The three biggest are:
- .dict() function is now renamed to .model_dump()
- schema_extra function within a Config class is now renamed to json_schema_extra
- Optional variables need a =None example: id: Optional[int] = None

----------------------
SQL database overview. 

What is a database? 
- Organized collection of structured information of data, which is stored in a computer system. 
- can be easily accessed. 
- can be modified
- can be controlled and organized
- Many databases use a structed query language (SQL) to modify and write data. 

What is a database? 
- Data can be related to just about any object. 
- For example, a user on an application may have: 
    - Name
    - Age
    - Email
    - Password

A database is a collection of data. 
A database allows management of this data.
Databases are organized in how data can be retrieved, stored, and modified. 

There are many types of Database MAangement Systems (DBMS), including:
- SQLite
- PostgreSQL
- MySQL

Waht is a SQL
- Pronounced "S-Q-L" or "Sequel"
- Standard language for dealing with relational databases.
- SQL can be used to do different things with database records: 
    - Create
    - Read
    - Update
    - Delete

CRUD operations in SQL correspond to these actions:
- Create: INSERT
- Read: SELECT
- Update: UPDATE
- Delete: DELETE

We need to install SQLAlchemy to interact with SQL databases in our FastAPI project.

To install SQLAlchemy, run the following command:
```bash
pip install sqlalchemy
```

You need to install SQLite3 from https://sqlite.org/download.html and add it to your system's PATH.
To do this: 
1. Download the appropriate version of SQLite3 for your operating system from the official website.
    - For windows you want the sqlite-tools-win32-x64-*.zip file.
2. Extract the downloaded files to a directory of your choice.
3. Add the directory containing the SQLite3 executable to your system's PATH environment variable.
    - To do this on Windows, open the Start menu, search for "Environment Variables," and select "Edit the system environment variables." In the System Properties window, click the "Environment Variables" button. In the Environment Variables window, find the "Path" variable under "System variables," select it, and click "Edit." Add the directory containing the SQLite3 executable to the list of paths and click "OK" to save the changes.
4. Verify the installation by opening a terminal or command prompt and running `sqlite3 --version`. You should see the installed version of SQLite3.

SQL Queries
Inserting Database Tables (TODOS)
```sql
INSERT INTO todos (title, description, priority, complete)
VALUES ('Go to store', 'To pickup eggs', 4 , False);

INSERT INTO todos (title, description, priority, complete)
VALUES ('Haircut', 'Need to get length 1mm', 3 , False);

INSERT INTO todos (title, description, priority, complete)
VALUES ('Feed dog', 'Make sure to use new food brand', 2 , False);

INSERT INTO todos (title, description, priority, complete)
VALUES ('Water plant', 'Inside and outside plants', 1 , False);

INSERT INTO todos (title, description, priority, complete)
VALUES ('Learn something new', 'Learn to program', 5 , False);
    
INSERT INTO todos (title, description, priority, complete)
VALUES ('Shower', 'Havent showered in 5 days', 1 , False);
```

Select SQL Queries
```sql
SELECT * FROM todos;
```

In SQL, the * symbol is used to select all columns from a table. For example, `SELECT * FROM todos;` retrieves all columns for all rows in the `todos` table.

What if we only want the titles

```sql
SELECT title FROM todos;
```

If we want the descriptions only:
```sql
SELECT description FROM todos;
```

If we want to select both the title and description:
```sql
SELECT title, description FROM todos;
```

If we want priority as well: 
```sql
SELECT title, description, priority FROM todos;
```

Now about the WHERE clause in SQL.
The WHERE clause is used to filter records based on a specified condition. For example, if we want to select todos with a priority of 1:

```sql
SELECT * FROM todos WHERE priority = 5;
```
```sql
SELECT * FROM todos WHERE title="Feed dog";
```

The main use for Where clause is to filter records based on specific conditions, allowing you to retrieve only the rows that meet the criteria you specify.
```sql
SELECT * FROM todos WHERE id = 2;
```

Now the UPDATE statement in SQL.
The UPDATE statement is used to modify existing records in a table. For example, if we want to update the priority of the todo with id 2:
```sql
UPDATE todos SET complete=True WHERE id = 5;
```

You should always use the primary key (usually the `id` column) in the WHERE clause when updating records to ensure that you are modifying the correct row.
```sql
UPDATE todos SET complete=True WHERE title='Learn something new';
```
The issue with the above is that multiple records could be set to true. 

Now the Delete clause
```sql
DELETE FROM todos WHERE id = 5;
```

If you write:
```sql
DELETE FROM todos WHERE complete=0;
```
You run the risk of deleting multiple records unintentionally, especially if many todos have `complete=0`. Always be cautious with DELETE statements and consider using the primary key in the WHERE clause to target specific rows.


