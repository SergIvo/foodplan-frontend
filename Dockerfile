FROM python:3.10

ENV PYTHONUNBUFFERED 1
RUN mkdir food-plan-front

COPY . foodplan-front
WORKDIR /foodplan-front

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

RUN pwd
RUN cd app
RUN ls

CMD ["python3", "app/manage.py", "runserver", "0.0.0.0:8000"]
