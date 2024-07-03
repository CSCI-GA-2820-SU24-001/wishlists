# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


## Overview
This project implements the wishlists service, which allows customers to make a collection of products products that they wish they had the money to purchase. The service includes a REST API that provides CRUD operations for managing wishlists and wishlist items.

## Contents
The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── routes.py              - module with service routes
├── models                 - module with business models
    |── __init__.py        - package initializer
    |── persistent_base.py - Base class
    |── wishlist_item.py   - Item class
    |── wishlist.py        - Wishlist class
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```
## API Endpoints
The wishlists service provides the following API endpoints:

| Operation                         | Method | URL                                          |
|-----------------------------------|--------|----------------------------------------------|
| **List all wishlists**            | GET    | `/wishlists`                                 |
| **Create a wishlist**             | POST   | `/wishlists`                                 |
| **Read a wishlist**               | GET    | `/wishlists/{id}`                            |
| **Update a wishlist**             | PUT    | `/wishlists/{id}`                            |
| **Delete a wishlist**             | DELETE | `/wishlists/{id}`                            |
| **List all items in a wishlist**  | GET    | `/wishlists/{id}/items`                      |
| **Create an item in a wishlist**  | POST   | `/wishlists/{id}/items`                      |
| **Read an item in a wishlist**    | GET    | `/wishlists/{id}/items/{id}`                 |
| **Update an item in a wishlist**  | PUT    | `/wishlists/{id}/items/{id}`                 |
| **Delete an item in a wishlist**  | DELETE | `/wishlists/{id}/items/{id}`                 |


## Running the Tests

To run the tests for this project, you can use the following command:

```bash
make test
```

This command will run the test suite using `pytest` and ensure that all the tests pass.

## Running the Service

To run the wishlists service locally, you can use the following command:

```bash
flask run
```

The service will start and be accessible at `http://localhost:8000`. To change the port, update the environment variable in the `.flaskenv` file.


## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
