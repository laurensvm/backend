# backend

### Installation
1. Clone project
2. `cd /path/to/root/`
3. Create virtual environment
4. `pip install -r requirements.txt` 
5. Inside the virtual env, enter command `python application.py`

### Usage 

### Routes
+ Authentication Routes
  + `/auth/token/` GET
    + returns: `{ 'token': Token, 'expiration': Int }`
  + `/auth/users/` GET
    + args: `?amount=0`
    + returns: `{ 'users': [User] }`
  + `/auth/users/<int:id>/` GET
    + returns: `{ User }`
  + `/auth/users/<string:username/` GET
    + returns: `{ User }`
  + `/auth/users/create/` POST
    + json: `{ 'username': String, 'email': String, 'password': String }`
    + returns: `{ 'success': String, 'message': String }`
  + `/auth/users/delete/<string:username/` GET
    + returns: `{ 'success': String, 'message': String }`
  + `/auth/users/delete/<int:id/` GET
    + returns: `{ 'success': String, 'message': String }`
+ Directory Routes
  + `/directories/` GET/POST (DEPRECATED)
    + json: `{ 'path': String } (POST)`
    + args: `?amount=0 (GET)`
    + returns: `{}`
  + `/directories/<int:id>/`
    + returns `{ Directory }`
  + `/directories/<int:id/files/`
    + returns `{ 'files': [File] }`
  + 
+ File Routes
  + TO-DO
+ Image Routes
  + TO-DO
+ Video Routes
  + TO-DO

