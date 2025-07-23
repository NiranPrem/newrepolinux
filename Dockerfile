FROM nginx:alpine

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy frontend files to nginx folder
COPY web/ /usr/share/nginx/html/

# Copy backend app.py somewhere inside container (e.g., /app)
COPY app.py /app/app.py

# Expose port 80 for nginx
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

