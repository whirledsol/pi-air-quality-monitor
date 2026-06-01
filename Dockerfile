FROM python:3.14.5
WORKDIR /code
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src .
#ENTRYPOINT [ "python" ]
#CMD [ "app.py" ]
CMD ["python","-u","app.py"]
