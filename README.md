# My Django Project
This project is a Django-based web application. It includes features like book rating and recommendations. The application uses PostgreSQL as its database and is containerized with Docker for easy setup and deployment.

## Features
- Book recommendations
- Responsive design using Tailwind CSS
- Environment-based configuration using .env files

## Prerequisites
Before you begin, ensure you have the following installed on your local machine:

- Docker
- Docker Compose
- Python 3.x (optional, if you want to run without Docker)

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/ProsteMato/book-recommendation-app.git
cd book-recommendation-app
```

### Set Up the Environment Variables
A sample `.env.example` file is provided in the root of the project. You can copy this file to create your own `.env` file, which will store environment-specific variables such as database credentials and secret keys.

```bash
cp .env.example .env
```

Then, edit the `.env` file to match your environment configuration.

Here is an example of what your .env file might look like:

```bash
DATABASE_NAME=mydatabase
DATABASE_USER=myuser
DATABASE_PASSWORD=mypassword
DATABASE_HOST=db
DATABASE_PORT=5432
DEBUG=True
SECRET_KEY=your-secret-key
KAGGLE_USERNAME=your-secret-username
KAGGLE_KEY=your-secret-kaggle-key
```

### Build and Run the Docker Containers
Use Docker Compose to build and run the project:

For development enviroment:

```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

This command will:

- Build the Docker images for your Django app and PostgreSQL database.
- Start the containers in the background.
###  Apply Migrations
Once the containers are up and running, apply the migrations to set up your database schema:

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### Download the data
Data are located in `myproject/data/dataset` directory. They are already downloaded but if you like to download them by yourself. You can do it by writing an command:

```bash
docker-compose -f docker-compose.dev.yml exec web python ./myproject/download_data.py
```

For this command to work properly you need to have set kaggle enviroment variables in `.env` file.

### Transform the data
Transformed data are located in `myproject/data/postprocess` directory. They are already transformed but if you like to transform them by yourself. You can do it by writing an command:

```bash
docker-compose -f docker-compose.dev.yml exec web python ./myproject/transform_data.py
```

### Import the data
To import data to database you can run command:
```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py import_data
```

### Access the Application
Once everything is set up, you can access the application by navigating to:

Application: http://localhost:8000

### Stopping the Containers
To stop the containers, use:

```bash
docker-compose -f docker-compose.dev.yml down
```

This command will stop and remove the containers but will preserve your database data.

### Development
Installing Additional Python Packages
If you need to install additional Python packages, use:

```bash
docker-compose -f docker-compose.dev.yml exec web pip install package-name
```

Then, update the requirements.txt file:

```bash
docker-compose -f docker-compose.dev.yml exec web pip freeze > requirements.txt
```

### Accessing the Django Shell
You can access the Django shell within the Docker container:

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py shell
```

### Deployment
For production deployment, make sure to:

Set DEBUG=False in your .env file.
Securely configure your SECRET_KEY and database credentials.
Use a production-ready web server like Gunicorn and configure it in your Dockerfile.

### Contributing
If you'd like to contribute to this project, please fork the repository and use a feature branch. Pull requests are warmly welcome.

### License
This project is licensed under the MIT License. See the LICENSE file for details.