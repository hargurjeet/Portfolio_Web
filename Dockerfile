FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Strip Windows line endings and set executable — belt and braces
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]