#!/bin/bash

# Start FastAPI in the background
uvicorn appAPI:app --host 0.0.0.0 --port 8000 &

# Start Streamlit in the foreground
streamlit run appStreamlit.py --server.port 8501 --server.address 0.0.0.0