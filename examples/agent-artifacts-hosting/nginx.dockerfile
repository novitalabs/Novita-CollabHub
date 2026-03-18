FROM ubuntu:22.04
RUN apt-get update && \\
    apt-get install -y nginx && \\
    apt-get clean && \\
    rm -rf /var/lib/apt/lists/*
RUN rm -rf /var/www/html/*
COPY . /var/www/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]