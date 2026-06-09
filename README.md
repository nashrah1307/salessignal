## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL installed locally

### 1. Clone the repo
git clone https://github.com/YOURUSERNAME/salessignal.git
cd salessignal

### 2. Create Python virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r backend/requirements.txt

### 3. Set up environment variables
Copy backend/.env.example to backend/.env and fill in your values:
- DATABASE_URL: your local PostgreSQL connection string
- GROQ_API_KEY: free key from console.groq.com

### 4. Set up the database
Run these in order:
python load_data.py
python feature_engineering.py
python train_model.py
python benchmarking.py
python backend/database/models.py

### 5. Run backend
cd backend
uvicorn main:app --port 8001

### 6. Run frontend
cd frontend
npm install
npm run dev

Dashboard runs at http://localhost:5173 or 5174
Backend API at http://localhost:8001
