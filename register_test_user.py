import requests
import json

# Test user details
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

try:
    # Register the user using JSON data
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json=test_user,
        headers=headers
    )
    
    if response.status_code == 200:
        print("Test user created successfully!")
        print(f"Email: {test_user['email']}")
        print(f"Password: {test_user['password']}")
    else:
        print(f"Error creating user: {response.status_code}")
        print(response.text)
        
        # If user already exists, try logging in
        if "already registered" in response.text.lower():
            print("\nTrying to log in with existing user...")
            login_response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                data={
                    "username": test_user["email"],
                    "password": test_user["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if login_response.status_code == 200:
                print("\nLogin successful!")
                print(f"Access token: {login_response.json().get('access_token')}")
            else:
                print("\nLogin failed:", login_response.text)

except Exception as e:
    print(f"An error occurred: {str(e)}")
    print("Make sure the server is running on http://localhost:8000")
