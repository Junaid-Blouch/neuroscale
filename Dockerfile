# Using Python 3.11 base image
FROM python:3.11

# Setting the working directory
WORKDIR /code

# Copying the requirements file and installing packages
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copying the entire project code
COPY . .

# Hugging Face uses port 7860 by default, so we run Uvicorn on it
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]