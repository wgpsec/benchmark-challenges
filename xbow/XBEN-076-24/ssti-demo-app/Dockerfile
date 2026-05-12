FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

RUN apt-get update -y

RUN apt-get install -y curl

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
