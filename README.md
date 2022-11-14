# NYU DevOps Project Template
[![Build Status](https://github.com/CSCI-GA-2820-FA22-001/customers/actions/workflows/tdd-tests.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-001/customers/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## API Calls Available 
#### 1. ADD A NEW CUSTOMER  (POST)
### Request
```
{
  "first_name": "John",
  "last_name": "Doe",
  "active": true,
  "addresses": [{
  
  "name": "home",
  "street": "4th St",
  "city": "New York",
  "state": "NY",
  "postalcode": "10003"
  }]
}
```

### Response

```
{
  "active": true,
  "addresses": [
    {
      "city": "New York",
      "customer_id": 400,
      "id": 1,
      "name": "home",
      "postalcode": "10003",
      "state": "NY",
      "street": "4th St"
    }
  ],
  "first_name": "John",
  "id": 400,
  "last_name": "Doe"
}

```
#### 2. RETRIEVE A CUSTOMER (GET /id)

To `retrieve` a single customer with the respective id, use:

```
http://localhost:8000/customers/id
```

### Response
```
{
  "active": true,
  "addresses": [
    {
      "city": "New York",
      "customer_id": 400,
      "id": 1,
      "name": "home",
      "postalcode": "10003",
      "state": "NY",
      "street": "4th St"
    }
  ],
  "first_name": "John",
  "id": 400,
  "last_name": "Doe"
}
```
#### 3. LIST ALL CUSTOMERS  (GET)

To `list all` customers, use:

```
http://localhost:8000/customers
```

### Response
```
[
  {
    "active": true,
    "addresses": [
      {
        "city": "New York",
        "customer_id": 401,
        "id": 3,
        "name": "home",
        "postalcode": "10003",
        "state": "NY",
        "street": "4th St"
      }
    ],
    "first_name": "John",
    "id": 401,
    "last_name": "Doe"
  },
  {
    "active": true,
    "addresses": [
      {
        "city": "New York",
        "customer_id": 402,
        "id": 4,
        "name": "home",
        "postalcode": "10003",
        "state": "NY",
        "street": "4th St"
      }
    ],
    "first_name": "John",
    "id": 402,
    "last_name": "Doe2"
  },
  {
    "active": true,
    "addresses": [
      {
        "city": "New York",
        "customer_id": 403,
        "id": 5,
        "name": "home",
        "postalcode": "10003",
        "state": "NY",
        "street": "4th St"
      }
    ],
    "first_name": "John",
    "id": 403,
    "last_name": "Doe3"
  }
]
```
#### 4. DELETE A CUSTOMER   (DELETE /id)
No body is required. `Status` returned:
```
204 NO CONTENT
```
#### 5. UPDATE AN EXISTING CUSTOMER (PUT/id)

### Request
```
{
  "first_name": "John",
  "last_name": "Doe",
  "active": false,
  "addresses": [{
  
  "name": "home",
  "street": "4th St",
  "city": "New York",
  "state": "NY",
  "postalcode": "10003"
  }]
}
```

### Response
```
{
  "active": false,
  "addresses": [
    {
      "city": "New York",
      "customer_id": 400,
      "id": 1,
      "name": "home",
      "postalcode": "10003",
      "state": "NY",
      "street": "4th St"
    },
    {
      "city": "New York",
      "customer_id": 400,
      "id": 2,
      "name": "home",
      "postalcode": "10003",
      "state": "NY",
      "street": "4th St"
    }
  ],
  "first_name": "John",
  "id": 400,
  "last_name": "Doe"
}
```
## How To Test
To test the code from the VScode terminal, run: 
```
nosetests
```
To see the lines that were not tested in the coverage report, use:
```
coverage report -m
```


## How To Run
To start the service in the VScode terminal write:
``` 
honcho start 
```

If Thunder Client is not readily available:

To run the service internally, you can use the extension "Thunder Client". It can be downloaded by naviagting to "extensions" tab in VScode and searching for "Thunder CLient".

Once in the client, user can choose between
```
GET
POST
PUT
DELETE
```
followed by: 
```
http://localhost:8000/customers
```

NOTE: In POST & PUT, JSON content with the desired information needs to be inserted in the body. 

### Using Curl Command

Alternatively, we can see our calls response using curl in the terminal. To see the headers, use:
```
curl -i http://localhost:8000/customers
```
## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
