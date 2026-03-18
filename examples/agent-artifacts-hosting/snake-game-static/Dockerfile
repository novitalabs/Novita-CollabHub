FROM nginx:alpine

# Clean default pages
RUN rm -rf /usr/share/nginx/html/*

# Copy website files
COPY . /usr/share/nginx/html/

# Change file permissions to allow nginx to read
RUN chmod -R 755 /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
