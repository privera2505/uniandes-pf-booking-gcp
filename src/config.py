from os import getenv

REPOSITORY_IMPL = getenv("REPOSITORY_IMPL", "memory")
APP_HOST = getenv("APP_HOST", "0.0.0.0")
APP_PORT = getenv("APP_PORT", "8000")
INSTANCE_CONNECTION_NAME = getenv("INSTANCE_CONNECTION_NAME","secret-lambda-491419-p2:us-central1:test-search-services")
DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = getenv("DB_PORT", "5432")
DB_USER = getenv("DB_USER","postgres")
DB_NAME = getenv("DB_NAME","postgres")
DB_PASSWORD = getenv("DB_PASSWORD","Postgres1.")
ENVIRONMENT = getenv("ENVIRONMENT", "dev")
ALLOWED_ORIGINS = getenv("ALLOWED_ORIGINS", "*").split()