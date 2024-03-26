## Activating the Virtual Environment

Activate the virtual environment using the appropriate command for your operating system.

### On Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

## Installing Packages

With the virtual environment activated, you can install packages using uv. Here's how:

```bash
pip install -r requirements.txt  # Install from a requirements.txt file.
```

## Run Application

```bash
uvicorn Project2_books_apis:app --reload
```

