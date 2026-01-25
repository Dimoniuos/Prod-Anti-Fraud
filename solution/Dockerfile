FROM python:3.12.1-alpine3.19

WORKDIR /app

RUN apk add --no-cache curl

COPY solution /app/solution
COPY solution/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
ENV SERVER_PORT=8080

CMD ["sh", "-c", "exec uvicorn solution.app:app --host=0.0.0.0 --port=$SERVER_PORT"]