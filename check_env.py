import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Print all environment variables
print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith('POSTGRES_') or key.startswith('DATABASE_'):
        print(f"{key}: {value}")

# Check if SQLALCHEMY_DATABASE_URI is set
print("\nChecking SQLALCHEMY_DATABASE_URI:")
print(f"SQLALCHEMY_DATABASE_URI: {os.getenv('SQLALCHEMY_DATABASE_URI')}")

# Check if DATABASE_URL is set
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Check if .env file exists
print("\nChecking .env file:")
if env_path.exists():
    print(f".env file exists at: {env_path}")
    print("Contents of .env file:")
    with open(env_path, 'r') as f:
        print(f.read())
else:
    print(".env file does not exist")
