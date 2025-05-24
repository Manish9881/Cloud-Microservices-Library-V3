FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5002
CMD ["python", "main.py"]
#CMD ["sh", "-c", "sleep 10 && python main.py"]
