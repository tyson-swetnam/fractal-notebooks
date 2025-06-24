# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Streamlit uses
EXPOSE 8501

# Run the command to start Streamlit when the container launches
CMD ["streamlit", "run", "apps/branching_tree.py"]
