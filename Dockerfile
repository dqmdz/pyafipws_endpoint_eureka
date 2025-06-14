# Build stage
FROM python:3.11-alpine AS builder

RUN apk update && apk add git
RUN git clone --branch v2025.05.05 --single-branch https://github.com/dqmdz/pyafipws.git
WORKDIR /pyafipws
RUN python -m pip install --upgrade pip
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
RUN if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

RUN python setup.py install


# Final stage
FROM python:3.11-alpine

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages/PyAfipWs* /usr/local/lib/python3.11/site-packages/

COPY requirements.txt ./

RUN apk update && apk add bash
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Copia los archivos secretos
COPY user.crt user.crt
COPY user.key user.key

ENV FLASK_APP=app.service
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=${INSTANCE_PORT:-5000}
ENV FLASK_DEBUG=1
ENV FLASK_ENV=development

CMD ["sh", "-c", "flask run --host=0.0.0.0 --port=${INSTANCE_PORT:-5000} --debug"]
