FROM python:3.7.4-buster
COPY . /elth
COPY requirements.txt /
RUN pip install -r /requirements.txt
WORKDIR /elth
EXPOSE 8001

CMD ["gunicorn", "--bind", "0.0.0.0:8001", "elth.wsgi"]