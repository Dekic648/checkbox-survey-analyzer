
# Use an official Python runtime as base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Copy app files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose default HF Space port
EXPOSE 7860

# Start the Dash app
CMD ["python", "dash_survey_app.py"]
