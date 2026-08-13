# BrewPredict: Tea Management & ML Prediction API

A high-performance, fully documented FastAPI REST API for managing tea products (CRUD operations) and serving machine learning predictions using a trained Scikit-Learn model.

---

📌 Project Overview

The Tea & ML Prediction API provides two main functionalities:

1. Tea Management API

Create a tea

Retrieve all teas

Retrieve a specific tea

Update a tea

Delete a tea



2. Machine Learning Prediction API

Accept numerical input features

Pass the features to a trained ML model

Return the model's prediction




The project is built using Python and FastAPI and can be easily extended with a database, authentication, frontend, or cloud deployment.


---

🚀 Features

Tea Management

Method	Endpoint	Description

GET	/	Check API status
GET	/teas	Get all teas
GET	/teas/{tea_id}	Get a specific tea
POST	/teas	Create a new tea
PUT	/teas/{tea_id}	Update an existing tea
DELETE	/teas/{tea_id}	Delete a tea


Machine Learning

Method	Endpoint	Description

POST	/predict	Generate an ML prediction



---

🛠️ Technologies Used

Python 3.10+

FastAPI

Pydantic

Uvicorn

Joblib

Scikit-learn — for the trained ML model

REST API

Swagger/OpenAPI



---

📂 Project Structure

A recommended project structure is:

tea-ml-api/
│
├── main.py
├── model.pkl
├── requirements.txt
├── README.md
│
└── .gitignore

Files

main.py

Contains the FastAPI application, API routes, Pydantic models, CRUD operations, and ML prediction endpoint.

model.pkl

Contains the trained machine-learning model saved using joblib.

requirements.txt

Contains all Python dependencies required to run the application.

README.md

Project documentation.

.gitignore

Prevents unnecessary files such as virtual environments and cache files from being committed to Git.


---

⚙️ Installation

1. Clone the Repository

git clone <your-github-repository-url>
cd tea-ml-api


---

2. Create a Virtual Environment

Windows

python -m venv venv
venv\Scripts\activate

macOS/Linux

python3 -m venv venv
source venv/bin/activate


---

3. Install Dependencies

Create a requirements.txt file:

fastapi
uvicorn
pydantic
joblib
scikit-learn

Then install:

pip install -r requirements.txt


---

▶️ Running the Application

Start the FastAPI development server:

uvicorn main:app --reload

You should see something similar to:

Uvicorn running on http://127.0.0.1:8000

The API is now available at:

http://127.0.0.1:8000


---

📖 API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI

Open:

http://127.0.0.1:8000/docs

Swagger UI allows you to:

View available endpoints

Enter request data

Execute API requests

View responses

Test CRUD operations


ReDoc

FastAPI also provides ReDoc:

http://127.0.0.1:8000/redoc


---

🏠 1. Root Endpoint

Request

GET /

Response

{
  "message": "Welcome to the Tea API!",
  "status": "running"
}

This endpoint can be used as a basic health/status check.


---

🍵 2. Get All Teas

Request

GET /teas

Example Response

[
  {
    "name": "Green Tea",
    "flavor": "Mint",
    "price": 120
  },
  {
    "name": "Black Tea",
    "flavor": "Masala",
    "price": 150
  }
]


---

🔎 3. Get a Single Tea

Request

GET /teas/0

The tea_id represents the index of the tea in the current in-memory list.

Response

{
  "name": "Green Tea",
  "flavor": "Mint",
  "price": 120
}

If the tea doesn't exist:

{
  "detail": "Tea not found"
}

The API returns HTTP status:

404 Not Found


---

➕ 4. Create a Tea

Request

POST /teas

Request Body

{
  "name": "Green Tea",
  "flavor": "Mint",
  "price": 120
}

Response

{
  "name": "Green Tea",
  "flavor": "Mint",
  "price": 120
}

The endpoint returns:

201 Created


---

✏️ 5. Update a Tea

Request

PUT /teas/0

Request Body

{
  "name": "Premium Green Tea",
  "flavor": "Lemon",
  "price": 180
}

Response

{
  "name": "Premium Green Tea",
  "flavor": "Lemon",
  "price": 180
}


---

🗑️ 6. Delete a Tea

Request

DELETE /teas/0

Response

{
  "name": "Premium Green Tea",
  "flavor": "Lemon",
  "price": 180
}

If the specified tea does not exist:

{
  "detail": "Tea not found"
}


---

🤖 7. Machine Learning Prediction

The /predict endpoint connects the FastAPI application to a trained machine-learning model.

Endpoint

POST /predict

Request Body

{
  "data": [5.1, 3.5, 1.4, 0.2]
}

The API sends the input to:

model.predict([request.data])

Example Response

{
  "prediction": 0
}

The exact prediction depends on the trained model.


---

🧠 ML Model Integration

The application loads a trained model using:

import joblib

model = joblib.load("model.pkl")

The trained model should be stored as:

model.pkl

For example, a scikit-learn model can be saved using:

import joblib

joblib.dump(model, "model.pkl")

And loaded later using:

model = joblib.load("model.pkl")


---

📊 Prediction Data

The input features supplied to /predict must match the features used while training the model.

For example, if the model was trained with four features:

Feature 1
Feature 2
Feature 3
Feature 4

then the request should contain:

{
  "data": [5.1, 3.5, 1.4, 0.2]
}

Sending an incorrect number of features may cause the model to return an error.


---

✅ Data Validation

Pydantic is used to validate incoming data.

The Tea model:

class Tea(BaseModel):
    name: str
    flavor: str
    price: float

The enhanced version also validates:

name: str = Field(..., min_length=1)
flavor: str = Field(..., min_length=1)
price: float = Field(..., gt=0)

Therefore:

Tea name cannot be empty.

Flavor cannot be empty.

Price must be greater than 0.


For example, this is invalid:

{
  "name": "",
  "flavor": "Mint",
  "price": -10
}

FastAPI automatically returns a validation error.


---

🔐 Error Handling

The application uses HTTPException for API errors.

Example:

raise HTTPException(
    status_code=404,
    detail="Tea not found"
)

Common HTTP status codes:

Status	Meaning

200	Successful request
201	Resource created
400	Bad request
404	Resource not found
500	Internal server error



---

🗃️ Current Data Storage

The current implementation uses:

teas: List[Tea] = []

This means the tea data is stored in memory.

Important limitation

All tea data will be lost when the FastAPI application restarts.

For example:

Application starts
       ↓
Tea data stored in memory
       ↓
Application stops
       ↓
Tea data is lost

For a production application, this should be replaced with a database such as:

SQLite

PostgreSQL

MySQL

MongoDB



---

🔄 API Architecture

The basic architecture is:

Client
  │
  │ HTTP Request
  ▼
FastAPI
  │
  ├── Tea CRUD Operations
  │       │
  │       ▼
  │   Tea Data
  │
  └── /predict
          │
          ▼
      ML Model
          │
          ▼
      Prediction


---

🧪 Testing

You can test the API using:

Swagger UI

http://127.0.0.1:8000/docs

You can also use:

Postman

Insomnia

curl

Python requests

Frontend applications


Example using curl:

curl http://127.0.0.1:8000/teas


---

🔧 Example Complete Workflow

Step 1 — Start API

uvicorn main:app --reload

Step 2 — Create tea

POST /teas

{
  "name": "Green Tea",
  "flavor": "Mint",
  "price": 120
}

Step 3 — Retrieve teas

GET /teas

Step 4 — Update tea

PUT /teas/0

Step 5 — Delete tea

DELETE /teas/0

Step 6 — Make prediction

POST /predict

{
  "data": [5.1, 3.5, 1.4, 0.2]
}


---

🛡️ Security Considerations

For production use, consider adding:

JWT authentication

API keys

HTTPS

CORS configuration

Rate limiting

Input sanitization

Environment variables for secrets

Proper database authentication

Logging and monitoring


Do not store passwords, API keys, or other secrets directly inside main.py.


---

🚀 Future Improvements

The project can be extended with:

Backend

PostgreSQL/MySQL database

SQLAlchemy

Alembic migrations

Authentication and authorization

JWT tokens

Pagination

Search and filtering

API versioning


Machine Learning

Multiple prediction models

Model versioning

Feature validation

Prediction probability

Model performance monitoring

MLflow integration


Frontend

A frontend can be developed using:

React.js

Angular

Vue.js

HTML/CSS/JavaScript


The frontend can communicate with the FastAPI backend through REST APIs.


---

📦 Requirements

Example requirements.txt:

fastapi
uvicorn
pydantic
joblib
scikit-learn

Install everything with:

pip install -r requirements.txt


---

🐛 Troubleshooting

ModuleNotFoundError: No module named 'fastapi'

Run:

pip install fastapi


---

uvicorn is not recognized

Run:

pip install uvicorn

or:

python -m uvicorn main:app --reload


---

FileNotFoundError: model.pkl

Make sure the model exists in the project directory:

tea-ml-api/
├── main.py
└── model.pkl


---

Prediction fails

Check that the number and order of input features match the data used to train the ML model.


---

👨‍💻 Author

Sagar Swami

Computer Engineering Graduate | Python | FastAPI | Machine Learning | Full-Stack Development


---

📄 License

This project is intended for learning, demonstration, and development purposes. You can add an appropriate open-source license such as MIT if you plan to distribute it publicly.


---

⭐ Project Highlights

This project demonstrates practical knowledge of:

Python
   ↓
FastAPI
   ↓
REST API
   ↓
Pydantic Validation
   ↓
CRUD Operations
   ↓
Machine Learning Model
   ↓
Prediction API
