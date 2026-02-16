# HomeAssignmentAPI

## Part I

Description
As a user, I want to be able to upload a CSV file to the server in order to store it there. 
To achieve this I need a backend endpoint.

Requirements:
- Github repository with basic FastAPI structure
- API endpoint to upload a CSV file
- Unit tests for endpoint

Hints:
- Search the internet for common FastAPI project structure
- Do you know what is a cookiecutter?
- What HTTP method should you use and why?
- What is the best way to store uploaded CSV file?
- Search FastAPI documentation on how to work with files
- Check FastAPI docs on testing
- When writing tests, consider using `pytest` package and take advantage of special fixture objects
- Make sure to test if the uploaded file is saved correctly
- For manual testing use http://localhost:8000/docs

## Part II

Description
As a user, I want to be able to download a CSV file that I uploaded earlier.
For this, I need a backend endpoint.

Requirements:
- endpoint to download a file
- endpoint is tested

Hints:
- Which HTTP method should you use?
- Can you reuse the same endpoint, but with a different HTTP method?
- When developing, think of possible scenarios - what can go wrong?
- In Python you can define your own exceptions to handle specific problems
- Make sure to cover edge-cases in your tests
