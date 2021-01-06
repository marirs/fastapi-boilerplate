# fastAPI Biolerplate

A FastAPI project!

- Every endpoint should be accessed by an API key
- API key has roles, such a way that, access to appropriate endpoints is allowed or denied
- Multiple endpoint project
- User management to create new users, disable users, verify email accounts and then allow api access, etc...
- Connects to MongoDB

![](docs/fastAPIboilerplate.png)

---

A Rust version can be found [here](https://github.com/marirs/rocketapi).

---
#### Requirements

* fastAPI
* Python 3.7+

#### Lib Requirements

* UVLoop
* re2

#### Database

* MongoDB

#### Setting up
```
mkvirtualenv --python=/usr/bin/python3 fastapi-boilerplate
cd /path/to/project
setvirtualenvproject
```

#### Installing the requirements
```
pip install pipenv
pipenv install
```
OR
```
pip install -r requirements.txt
```

#### Creating the first user
```
$ ./first_user.py email@somemail.tld
Your API Key is: _hplIyYGpeVKc... (Do not loose this key as its not stored in the system)
```

#### Running the Project in Dev env
```
uvicorn server.main:app --reload
```

#### Project Structure

```
api/endpoints - handlers for all endpoint routes
core          - general components like settings, security, key validation, etc...
db            - db connection specific
db/crud       - CRUD for types from models
models        - pydantic models that used in crud or handlers
```

---
#### Docs

Accessing the "user" endpoint with non superuser account
```
$ curl -H'x-api-key: -OWN3pNZ6FsaPppPqsyeuF6sxe' -H'x-email-id: e@mail.tld' http://127.0.0.1:8000/api/user/ 

{
    "created_at": "2019-11-01T03:21:02.868000",
    "updated_at": "2019-11-06T03:22:01.045000",
    "email": "e@mail.tld"
}
```
Accessing the "user" endpoint with superuser account
```
$ curl -H'x-api-key: -OWN3pNZ6FsaPppPqsyeuF6sxe' -H'x-email-id: e@mail.tld' http://127.0.0.1:8000/api/user/ 
{
    "total_users": 1,
    "users": [
        {
            "created_at": "2019-11-01T03:21:02.868000",
            "updated_at": "2019-11-06T03:22:01.045000",
            "email": "e@mail.tld",
            "endpoint_access": [
                "user"
            ],
            "is_superuser": true,
            "is_active": true,
            "disabled": false,
            "hashed_api_key": "$2b$12$DJ2D249xR4MY.aeTODeq5OasBR8TUoxknjxX6WqLf1QoG1k7VWQim",
            "salt": "$2b$12$lJ937UATRjcCU4.kk0HYZ."
        }
    ]
}
```
Accessing the "hello" endpoint
```
$ curl -H'x-api-key: -OWN3pNZ6FsaPppPqsyeuF6sxe' -H'x-email-id: e@mail.tld' http://127.0.0.1:8000/api/hello/ 

"Hello World"
```
Verify an email account of an added API user account
```
$ curl http://127.0.0.1:8000/api/user/verify?email=marirs@gmail.com

{
    "detail": "e@mail.tld is now verified! You can start using your API key."
}
```
Disabling an email account
```
$ curl  -H'x-api-key: -OWN3pNZ6FsaPppPqsyeuF6sxe' -H'x-email-id: e@mail.tld' http://localhost:8000/api/user/disable?email=someone@gmail.com

{
    "detail": "someone@gmail.com is disabled!"
}
```
---
Initial Author: Sriram
