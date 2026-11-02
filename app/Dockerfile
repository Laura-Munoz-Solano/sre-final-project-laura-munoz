FROM python:3.12-slim

# Expose the Flask app port
EXPOSE 5000

# Set the working directory inside the container
WORKDIR /app

# Install Flask and the Prometheus client
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app.py .

# Set the default command to run the Flask app
CMD ["python", "app.py"]
