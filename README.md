# Customers

[![CI](https://github.com/CSCI-GA-2820-SU25-001/customers/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU25-001/customers/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU25-001/customers/graph/badge.svg?token=ADIP2ENTMG)](https://codecov.io/gh/CSCI-GA-2820-SU25-001/customers)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

The `/service` folder contains the `models.py` file for your model and a `routes.py` file for the customer service. The `/tests` folder has test case starter code for testing the model and the service separately.

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
├── models.py              - module with business models
├── routes.py              - module with service routes
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

## Available Calls

The Customer REST API Service provides the following endpoints:

### Root URL
- **GET /** - Returns information about the service and available paths
  - Returns: 200 OK with service information

### Health Check
- **GET /health** - Returns the health status of the service
  - Returns: 200 OK with "Healthy" message

### Customer Management

#### Create Customer
- **POST /customers** - Create a new customer
  - Content-Type: application/json
  - Request Body:
    ```json
    {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john.doe@example.com",
      "phone_number": "1234567890",
      "address": "123 Main St, City, State, ZIP"
    }
    ```
  - Returns: 201 CREATED with the created customer data and Location header

#### List Customers
- **GET /customers** - List all customers
  - Returns: 200 OK with list of all customers
- **GET /customers?email={email}** - Find a customer by email
  - Returns: 200 OK with matching customer or empty list if not found

#### Get Customer
- **GET /customers/{id}** - Get a customer by ID
  - Returns: 200 OK with customer data
  - Returns: 404 NOT FOUND if customer doesn't exist

#### Update Customer
- **PUT /customers/{id}** - Update a customer
  - Content-Type: application/json
  - Request Body: Same as Create Customer
  - Returns: 200 OK with updated customer data
  - Returns: 404 NOT FOUND if customer doesn't exist

#### Delete Customer
- **DELETE /customers/{id}** - Delete a customer
  - Returns: 204 NO CONTENT if successful
  - Returns: 204 NO CONTENT if customer doesn't exist (idempotent)

## Running and Testing the Code

### Prerequisites
- Python 3.9 or higher
- pip and pipenv installed
- Git

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customers
   ```

2. Set up Python virtual environment:
   ```bash
   pipenv install
   ```

3. Create a `.env` file by copying the example:
   ```bash
   cp dot-env-example .env
   ```

### Running the Service Locally

#### Using Honcho
The easiest way to run the service is using the Makefile:
```bash
make run
```

This uses Honcho to start the service, which will be available at http://localhost:8080.

#### Manual Run
Alternatively, you can run the service directly:
```bash
flask run
```

### Running Tests
To run all tests with coverage reporting:
```bash
make test
```

This will run all unit tests and generate a coverage report ensuring at least 95% code coverage.

### Development Commands

- **Install dependencies**:
  ```bash
  make install
  ```

- **Run linter**:
  ```bash
  make lint
  ```

- **Generate a new secret key**:
  ```bash
  make secret
  ```

### Docker and Kubernetes Deployment

#### Build Docker Image
```bash
make build
```

#### Push to Registry
```bash
make push
```

#### Deploy to Kubernetes (local development)
```bash
make cluster      # Create a local K3D Kubernetes cluster
make deploy       # Deploy the service to Kubernetes
```

#### Clean Up
```bash
make clean        # Remove Docker build cache
make cluster-rm   # Delete the Kubernetes cluster
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
# Test webhook
# Webhook test Fri Aug  1 20:24:17 UTC 2025
