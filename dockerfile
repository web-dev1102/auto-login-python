FROM python:3.7.9

ADD WebSiteLogin.py ./

RUN pip install --upgrade pip

Run pip install undetected-chromedriver requests mysql-connector-python

CMD ["python", "./WebSiteLogin.py"]