# Gestion Congés IA

A Django-based leave management system with AI-powered recommendations and chatbot support.

## Project Overview

This application provides a comprehensive solution for employee leave management with intelligent features:

- Employee leave request submission and tracking
- AI-powered leave approval recommendations based on workload predictions
- Automatic leave accrual calculation (1.83 days per month)
- HR dashboard for leave approval management
- Optional chatbot interface for employees

## Installation

### Prerequisites

- Python 3.10+ 
- pip (Python package manager)
- Virtual environment tool (venv recommended)

### Setup Steps

1. Clone the repository:
   ```powershell
   git clone <repository-url>
   cd app_conge_ia
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Create a `.env` file in the project root with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///db.sqlite3
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@example.com
   EMAIL_HOST_PASSWORD=your_app_password
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=your_email@example.com
   ```

4. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

5. Run migrations:
   ```powershell
   python manage.py migrate
   ```

6. Create a superuser:
   ```powershell
   python manage.py createsuperuser
   ```

7. Populate initial data (optional):
   ```powershell
   python setup_database.py
   ```

## Running the Application

### With Chatbot (Standard Mode)

To run the application with the chatbot functionality enabled:

```powershell
python manage.py runserver
```

This starts the Django development server at http://127.0.0.1:8000/ with all features enabled.

### Without Chatbot (Test Mode)

For testing routes without the chatbot functionality, use the specialized server script:

```powershell
python server_no_chatbot.py
```

This starts a Django server at http://127.0.0.1:8000/ using test settings that exclude the chatbot application and use SQLite for the database.

## Leave Accrual System

The system automatically calculates leave accruals using the formula:
```
Leave Accrued = (1.83 ÷ workable days in month) × days actually worked
```

### Running Accrual Calculations

For monthly accrual processing, use the management command:

```powershell
# Calculate accruals for previous month (default)
python manage.py accrue_leave

# Calculate for specific month and year
python manage.py accrue_leave --month 5 --year 2025

# Calculate and finalize (update employee balances)
python manage.py accrue_leave --month 5 --year 2025 --finalize
```

## API Endpoints

### Authentication
- `POST /api/register` - Register a new user
- `POST /api/login` - Login and get authentication token
- `GET /api/profile/` - Get current user profile

### Employee Management
- `GET /api/employees/` - List all employees
- `GET /api/employees/<id>/` - Get employee details
- `PATCH /api/employees/update/<id>/` - Update employee information
- `DELETE /api/employees/delete/<id>/` - Delete an employee

### Leave Requests
- `GET /api/demandes_conge/` - List all leave requests
- `POST /api/demande-conge/add/` - Submit a new leave request
- `GET /api/demande-conge/detail/<id>/` - Get leave request details
- `PUT /api/update-conge/update/<id>/` - Update a leave request
- `DELETE /api/demande-conge/delete/<id>/` - Delete a leave request
- `GET /api/demandes-conge/employe/<id>/` - Get all leave requests for an employee

### AI Recommendations
- `GET /api/demande-conge/recommandation/<id>/` - Get recommendation for a specific leave request
- `GET /api/recommandations/employe/<id>/` - Get all recommendations for an employee

### Leave Accrual
- `GET /api/leave-accruals/` - List all leave accrual records
- `GET /api/leave-accruals/<id>/` - Get specific accrual record
- `POST /api/leave-accruals/calculate/` - Calculate accrual for employee
- `POST /api/leave-accruals/finalize/` - Finalize accruals

## Gitignore Explanation

The `.gitignore` file excludes:

- **Python artifacts**: `__pycache__/`, `*.py[cod]`, `*$py.class`, etc.
- **Environment files**: `.env`, `venv/`, `.env.bak/`, etc.
- **Django files**: `*.log`, `db.sqlite3`, `media/`, etc.
- **Machine learning models**: `*.pkl` (except `workload_model.pkl`)
- **IDE settings**: `.idea/`, `.vscode/`, etc.
- **Media and static files**: `/media/`, `/static/`, etc.
- **Sensitive data**: `credentials.json`, `client_secret.json`, etc.

If you need to track new files that match these patterns, you'll need to modify the `.gitignore` file.

## Development Notes

- The workload prediction model (`workload_model.pkl`) calculates a score from 0-100 and makes recommendations:
  - Score > 75: "approuve" (recommended approval)
  - Score 50-75: "en_attente" (waiting/needs review)
  - Score < 50: "rejete" (recommended rejection)

- Leave accrual is calculated on a monthly basis at 1.83 days per month 
  - Adjusted proportionally for days worked vs. workable days
  - Requires HR finalization to be added to employee balances