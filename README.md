# Zap-Task: A Mini Freelance Service

[![CI/CD Pipeline](https://github.com/github-main-user/zap-task/actions/workflows/main.yml/badge.svg)](https://github.com/github-main-user/zap-task/actions/workflows/main.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Test Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/github-main-user/zap-task/actions/workflows/main.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Zap-Task is a full-featured REST API that simulates a freelance marketplace. It allows users to post tasks they need help with, and for other users (freelancers) to submit proposals to complete those tasks. This project is designed to showcase a robust backend implementation using modern Python and Django practices.

## Key Features

- **User Authentication**: Secure user registration and login system using JWT.
- **Task Management**: Clients can create, update, and manage tasks.
- **Proposal System**: Freelancers can browse tasks and submit proposals.
- **Review and Rating System**: Users can rate and review each other after a task is completed.
- **Payments**: Simulated payment processing for tasks.
- **Asynchronous Task Handling**: Background tasks for notifications and other operations.

## Tech Stack

- **Backend**: Python3.13, Django5+, Django REST Framework
- **Database**: PostgreSQL
- **Asynchronous Tasks**: Celery, Redis
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx
- **Testing**: Pytest
- **Dependency Management**: Poetry

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd zap-task
    ```

2.  **Set up environment variables:**
    Copy the example environment file and update it with your configuration.
    ```bash
    cp .env.example .env
    ```
    You will need to fill in the required variables in the `.env` file.

3.  **Build and run the application using Docker Compose:**
    ```bash
    docker compose up --build -d
    ```

4.  **(Optional) Create a superuser:**
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

The application should now be running at `http://localhost:80/`.

To stop started containers use `docker compose down`, add `-v` to clean up all volumes.

## API Documentation

Auto-generated Swagger/Redoc API documentation will be available at:

```
http://localhost/api/v1/docs/
http://localhost/api/v1/redoc/
```

## Running Tests

To run the test suite, use the following command:

```bash
docker compose -f compose.test.yml --env-file=.env.test up
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and continuous deployment. The pipeline is defined in `.github/workflows/main.yml` and consists of three main jobs:

1.  **Linting**: Checks the code for style and formatting issues using `flake8`, `black`, and `isort`.
2.  **Testing**: Runs the test suite using `pytest` in a Docker container.
3.  **Deployment**: Automatically deploys the application to a server when changes are pushed to the `main` branch.

This pipeline ensures that all code is tested and linted before being deployed, which helps to maintain code quality and prevent bugs.

## Project Structure

The project follows a standard Django layout with a dedicated `apps` directory to enforce modularity.

```
/apps
├───core/         # Core functionalities, tasks
├───payments/     # Payment processing logic
├───proposals/    # Handling proposals for tasks
├───reviews/      # User reviews and ratings
├───tasks/        # Task creation and management
└───users/        # User models, authentication, and profiles
```
