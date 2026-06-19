# Clone the repository
git clone <repo-url>
cd gifty-backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Add your API keys inside .env
# GROQ_API_KEY=your_key
# SERPER_API_KEY=your_key

# Run the backend
uvicorn app.main:app --reload