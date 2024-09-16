
# **Backend README (FastAPI)**
```markdown
Fruit.Ai Backend
This is the backend for the Fruit.Ai project, built using FastAPI. It handles the APIs for FAQs and other backend logic.
Hosted Link : https://fruitai-backend.onrender.com/

```
## Setup
1. Clone the repository:
    ```bash
    git clone <https://github.com/RaHuLShArMa-1403/fruitai-backend>
    cd fruitai-backend
    ```
2. Create a virtual environment and activate it:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows, use `env\Scripts\activate`
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```


4. Running the Project
1. To run the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```
2. The API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Environment Variables
Create a `.env` file in the root directory to define environment variables:



## Features
- **FAQs API:** Provides endpoints to perform CRUD operations on FAQs.
- **Authentication:** API endpoints for login and user management.
- **Scalable:** Uses FastAPI for building scalable APIs.

## Technologies
- FastAPI
- Python
- SQLite (or any other database you prefer)
- Uvicorn (for running the server)

## Project Structure
- `app/main.py`: Main file containing the API logic.
- `app/models`: Contains database models.
- `app/routers`: Contains API route handlers.
- `app/schemas`: Contains Pydantic models for data validation.

