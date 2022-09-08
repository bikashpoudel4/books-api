
Functioning RestAPI example.
    -Tech-stack:
        -Pthon
        -Django
        -Django-REST-Framework
        -PostgreSQL
        -Docker

BooksAPI which covers:
    -Test Driven Developement(TDD)
    -Super User Creation
    -User Registration
    -Token Authentication
    -Book Records:
            -GET
            -POST
            -DELETE
            -PUT
            -PATCH
    -Relational db
    -Image upload
    -Filtering
    -Unit Test

Useful commands:
    -To RUN the project:
        -   docker-compose up

    - Test Project:
        -   docker-compose run --rm app sh -c "python manage.py test" 
            -By using --rm our container is removed after test  

    - If problem with Pycopg2 or pycopg2 lib (PostgreSQL) :
        -   FIRST RUN:
            -   docker-compose down
                            OR
            -   docker-compose down --volumes 
        
        -   THEN RUN
            -   docker-compose up
                            OR
            -   docker-compose up --build
    
    -To create Super User
        -   docker-compose run app sh -c "python manage.py createsuperuser"
    
    -To make migrations 
        -   docker-compose run app sh -c "python manage.py makemigrations"
    
    -To make migrate 
        -   docker-compose run app sh -c "python manage.py migrate"
    
    -To create new app
        -   docker-compose run app sh -c "python manage.py startapp myapp"

The API is available at:
    -   http://127.0.0.1:8000
    -   localhost:8000

Some Urls:
    - To create user
        - http://localhost:8000/api/user/register/
    
    - Token
        - http://localhost:8000/api/user/token/

    - Books related urls
        - http://localhost:8000/api/books/
    
    - To record Book
        - http://localhost:8000/api/books/books/
    
    - To record tags
        - http://localhost:8000/api/books/tags/
    
    - To record Genre 
        - http://localhost:8000/api/books/genres/

    - To use filtering use(1 or 0) example on and off and can use (&) for different models
        - http://localhost:8000/api/books/genres/?assigned_only=1
    
    - To upload image
        - create instance which creates id and then
            - http://localhost:8000/api/books/books/1/upload-image/
                where 1 is a id
