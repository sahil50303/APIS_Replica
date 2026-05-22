# API Replication Server (FastAPI + Supabase)

This project replicates client HTTP APIs (both GET and POST endpoints) onto your own Supabase database. It secures incoming client requests using a custom API key authorization header (`X-API-Key`) and logs synced data in real-time.

An interactive **Developer Dashboard Hub** is built-in to let you manage API keys, explore interactive endpoint documentation, and view synced records.

---

## 📂 Project Structure

- `schema.sql`: Contains the PostgreSQL tables schema for your Supabase database.
- `main.py`: The FastAPI server containing endpoint logic, API key middleware, and Supabase connections.
- `requirements.txt`: Python package dependencies.
- `test_api.py`: A quick terminal-based testing script to verify the replication API end-to-end.
- `public/`: Assets for the admin dashboard frontend interface.

---

## ⚡ Quick Start

### 1. Database Setup
Copy the contents of [schema.sql](file:///c:/Users/Asus/OneDrive/Desktop/APISREPLICATE/schema.sql) and paste them into your **Supabase SQL Editor**, then run the query.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Rename `.env.example` to `.env` and fill in your Supabase database connection URL:
```env
DATABASE_URL=postgresql://postgres.[your-id]:[your-password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require
```

### 4. Run the Server
```bash
uvicorn main:app --reload
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser to access the Admin Dashboard.

### 5. Run Verification Test
```bash
python test_api.py
```

---

## 📄 License
This project is open-source and licensed under the MIT License.
