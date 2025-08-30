# 1. Clone/setup project
cd indian-stock-api-v2

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install PostgreSQL (if not installed)
# Ubuntu: sudo apt install postgresql postgresql-contrib
# Mac: brew install postgresql
# Windows: Download from postgresql.org

# 5. Install Redis (if not installed)
# Ubuntu: sudo apt install redis-server
# Mac: brew install redis
# Windows: Download from redis.io

# 6. Setup database and migrate data
python setup.py

# 7. Start Redis
redis-server

# 8. Run the FastAPI application
python main.py
