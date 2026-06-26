FROM m.daocloud.io/docker.io/library/python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY . .
RUN mkdir -p /app/data
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot.py"]
