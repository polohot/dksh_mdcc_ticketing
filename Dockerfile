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

# Install FastAPI server dependencies explicitly (in case they aren't in requirements.txt)
RUN pip install fastapi uvicorn

# Copy the rest of the app
COPY . .

# Make the startup script executable
RUN chmod +x run_services.sh

# Expose ports: 8000 for FastAPI, 8501 for Streamlit
EXPOSE 8000
EXPOSE 8501

# Run the startup script
CMD ["./run_services.sh"]