# oTree Survey — Setup & Running Instructions

## First-Time Setup (New System)

### 1. Install Anaconda
Download and install from https://www.anaconda.com if not already installed.

### 2. Create the Python Environment
```bash
conda create -n otree_env python=3.11
conda activate otree_env
```

### 3. Navigate to the Project Folder
```bash
cd /path/to/occupations
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
pip install otree --upgrade
```

### 5. Set Your OpenAI API Key
```bash
export OPEN_AI_KEY="sk-your-key-here"
```

To make it persistent across terminal sessions, add it to your shell profile:
```bash
echo 'export OPEN_AI_KEY="sk-your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 6. Delete Any Existing Database
Required when oTree has been updated or when running for the first time:
```bash
rm -f db.sqlite3
```

### 7. Start the Server
```bash
otree devserver
```

### 8. Open the App
Go to the following URL in your browser:
```
http://localhost:8000
```

---

## Restarting the Survey (Same System)

Each time you want to run the survey on a system that has already been set up:

> ⚠️ **Before deleting the database**, export and save your results from the previous session. Go to `http://localhost:8000/export` in the oTree admin panel and download all data as CSV before proceeding.

```bash
conda activate otree_env
cd /path/to/occupations
rm -f db.sqlite3
otree devserver
```

Then open `http://localhost:8000` in your browser.

---

## Troubleshooting

### `KeyError: 'OPEN_AI_KEY'`
The OpenAI API key is not set in the environment. Run:
```bash
export OPEN_AI_KEY="sk-your-key-here"
```
Then restart the server.

### `oTree has been updated. Please delete your database (db.sqlite3)`
The server will exit immediately. Delete the database and restart:
```bash
rm -f db.sqlite3
otree devserver
```

### Kernel or package errors in Cursor/Jupyter
Make sure you are using the `otree_env` kernel (Python 3.11), not the base Anaconda environment (Python 3.9).
