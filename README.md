# Library Service Project

A comprehensive REST API for library management, enabling books borrowing. Built with Django REST Framework and featuring JWT authentication.

## Installation using GitHub
Python 3.11 must be already installed  
git clone https://github.com/viktoriaom/library-service-project/  
cd library_service_project  

## Local Setup with SQLite
python3 -m venv venv  
source venv/bin/activate # *creates virtual environment on macOS/Linux*    
venv\Scripts\activate # *creates virtual environment on Windows*  
pip install -r requirements.txt  
python manage.py makemigrations # *creates migrations*    
python manage.py migrate # *creates DB*  
python manage.py runserver # *starts Django server*    

The API will be available at http://127.0.0.1:8000/  

#### Optional
Load test data into db:  
python manage.py loaddata library_fixture.json

## Run with Docker and PostgreSQL
docker-compose build  
docker-compose up  

The API will be available at `http://127.0.0.1:8002/

#### Optional
Load test data into db:  
docker-compose exec library python manage.py loaddata library_fixture.json

## Getting Access
* register a new user via api/user/register  
* get access token via api/user/token  
* include the token in your request headers:  
Authorize: Bearer "your-access-token"

#### Demo Credentials
For testing purposes only:  
**email:** first_user@library.com  
**password:** qazxsw


## Features
### Core functionality
* **Books Management** - Create and manage books
* **Borrowing System** - Borrowing & returning books


### Technical features
* **JWT Authentication** - Secure token-based authentication
* **Email-based Login** - Username field replaced with email
* **Advanced Filtering** - Filter by user or active borrowing
* **Role-based Permissions** - Custom permission classes
* **API Documentation** - Interactive Swagger/ReDoc docs
* **Comprehensive Tests** - Full test coverage for custom features
  

## Built With
* Django [https://www.djangoproject.com] - Web framework  
* Django REST Framework [https://www.django-rest-framework.org] - API toolkit  
* SQLite [https://sqlite.org] - Database  
* JWT [https://www.jwt.io] - Authentication
* drf-spectacular [https://drf-spectacular.readthedocs.io] - API documentation 
* Docker [https://www.docker.com] - Containerization 
* PostgreSQL [https://www.postgresql.org] - Database  


## Usage Tips
* Unauthorized users can list & retrieve books 
* Only authorized users can create borrowings
* Users can only access their own borrowings  
* Admins can access and filter all borrowings by user
* Admins & users can filter borrowings by active parameter
* Admins can create & update books
* Admins can delete all resources 
* Permissions are enforced on books views using custom BooksPermission permission class  
* Borrowings use standard IsAdminUser / IsAuthenticated permission classes
