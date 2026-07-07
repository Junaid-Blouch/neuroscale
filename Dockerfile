# 1. Use Python SLIM image to keep the container lightweight (fast boot)
FROM python:3.11-slim

# 2. IMPORTANT FOR HUGGING FACE: Create a non-root user (ID 1000)
# Hugging Face Spaces block root access for security.
RUN useradd -m -u 1000 user
USER user

# 3. Environment Variables
ENV PATH="/home/user/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 4. Set Working Directory
WORKDIR /code

# 5. Copy requirements and install them securely
COPY --chown=user:user ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 6. Copy the entire NeuroScale project
COPY --chown=user:user . /code/

# 7. Expose Port 7860 (Hugging Face Default)
EXPOSE 7860

# 8. Start the FastAPI Engine
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]