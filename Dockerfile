# Use official Python 3.12.12 image
FROM python:3.12.12

# Set work directory
WORKDIR /app
RUN mkdir -p /app/dksh_mdcc_ticketing

# Copy requirements first (to leverage Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose default uvicorn port
EXPOSE 8000

# Run streamlit
CMD ["streamlit", "run", "appStreamlit.py"]
