# File Manager Backend

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
    + returns: `{ 'token': String, 'expiration': Int }`
  + `/auth/users/` GET
    + args: `?amount=30`
    + returns: `{ 'users': [User] }`
  + `/auth/users/<int:id>/` GET
    + returns: `{ User }`
  + `/auth/users/<string:username>/` GET
    + returns: `{ User }`
  + `/auth/users/create/` POST
    + json: `{ 'username': String, 'email': String, 'password': String }`
    + returns: `{ 'success': String, 'message': String }`
  + `/auth/users/delete/<string:username>/` GET
    + returns: `{ 'success': String, 'message': String }`
  + `/auth/users/delete/<int:id>/` GET
    + returns: `{ 'success': String, 'message': String }`
    
+ Directory Routes
  + `/directories/` GET
    + args: `?amount=30`
    + returns: `{ 'directories' : [Directory]}`
  + `/directories/<int:id>/` GET
    + returns: `{ Directory }`
  + `/directories/<int:id/files/` GET
    + returns: `{ 'files': [File] }`
  + `/directories/<int:id>/rename/` POST
    + json: `{ 'name': String }`
    + returns: `{ 'success': String, 'message': String }`
  + `/directories/<int:id>/delete/` GET
    + returns: `{ 'success': String, 'message': String }`
  + `/directories/<int:id>/rights/` GET
    + returns: `{ 'users' : [ User ] }`
  + `/directories/root/` GET
    + returns: `{ Directory }`
  + `/directories/create/` POST
    + json: `{ 'path'/'name': String, 'parent_id': Integer }
    + returns: `{ 'success': String, 'message': String }
  + `/directories/id/` POST
    + json: `{ 'path': String }`
    + returns: `{ 'id': String }`
  + `/directories/delete/` POST
    + json: `{ 'path': String }` 
    + returns: `{ 'success': String, 'message': String }`
    
+ File Routes
  + `/files/` GET
    + args: `?amount=30`
    + returns: `{ 'files': [File] }`
  + `/files/` POST
    + json: `{ 'path': String }`
    + returns: `{ File }`
  + `/files/<int:id>/` GET
    + returns: `{ File }`
  + `/files/<string:username>/` GET
    + returns: `{ 'files': [File] }`
  + `/files/directory/` POST
    + json: `{ 'path'/'directory': String }`
    + returns: `{ 'files' : [File] }`
  + `/files/directory/<string:name>/` GET (name is not unique)
    + returns: `{ 'files' : [File] }`
  + `/files/directory/<int:id>/` GET
    + returns `{ 'files': [File] }`
  + `/files/<int:id>/delete/` GET
    + returns: `{ 'success': String, 'message': String }`
  + `/files/<int:id>/rename/` GET
    + returns: `{ 'success': String, 'message': String }`
  + `/files/download/<int:id>/` GET
    + returns: FileObject
  + `/files/download/` POST
    + json: `{ 'path': String }`
    + returns: `FileObject`
  + `/files/upload/` POST
    + form-data: `{ 'file': FileObject, 'directory_id': String }`
    + form-data (Optional): `{ 'type': String, 'description': String }`
   
+ Image Routes
  + `/images/` GET
    + args: `?amount=30`
    + returns: `{ 'images': [Image] }`
  + `/images/id/` GET
    + args: `?amount=30`
    + returns: `{ 'images': [Image.id] }`
  + `/images/<int:id>/` GET
    + returns: `{ Image }`
  + `/images/thumbnail/<int:id>/` GET
    + returns: `FileObject`
  + `/images/download/<int:id>/` GET
    + returns: `FileObject`
  + `/images/upload/` POST
    + form-data: `{ 'file': FileObject, 'directory_id': String }`
    + form-data (Optional): `{ 'type': String, 'description': String, 'latitude': Float, 'longitude': Float, 'device': String, 'resolution': String, 'local_id': String }`
    
+ Video Routes
  + `/videos/` GET
    + args: `?amount=30`
    + returns: `{ 'videos': [Video] }`
  + `/videos/id/` GET
    + args: `?amount=30`
    + returns: `{ 'videos': [Video.id] }`
  + `/videos/<int:id>/` GET
    + returns: `{ Video }`
  + `/videos/thumbnail/<int:id>/` GET
    + returns: `FileObject`
  + `/videos/length/<int:id>/` GET
    + returns: `{ 'length': Integer }`
  + `/videos/download/<int:id>/` GET
    + returns: `FileObject`
  + `/videos/upload/` POST
    + form-data: `{ 'file': FileObject, 'directory_id': String }`
    + form-data (Optional): `{ 'type': String, 'description': String, 'latitude': Float, 'longitude': Float, 'device': String, 'resolution': String, 'local_id': String, 'length': Integer }`

