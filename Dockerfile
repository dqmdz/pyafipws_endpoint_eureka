FROM python:3.10-alpine as builder

RUN apk update
RUN apk add git
RUN git clone https://github.com/reingart/pyafipws.git
WORKDIR /pyafipws
RUN python -m pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
RUN if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

RUN python setup.py install


# App
FROM python:3.10-alpine

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages/PyAfipWs* /usr/local/lib/python3.10/site-packages/

COPY requirements.txt ./

RUN apk update
RUN apk add bash
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8281

CMD ["flask", "--app", "app.service", "run", "--host", "0.0.0.0", "--port", "8281", "--debug"]
