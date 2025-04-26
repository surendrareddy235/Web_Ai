#official python image
FROM python:3.13-alpine

#set working directory
WORKDIR /app

#copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy all project files
COPY . .

#expose to the port 
EXPOSE 5000

#run the flask app
CMD ["python", "quartica.py"]

