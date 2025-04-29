FROM python:3.9-slim

# Create non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY --chown=user . .

# Expose the required port for Hugging Face Space
EXPOSE 7860

# Start Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "quartica:app"]