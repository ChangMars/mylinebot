FROM nginx:latest

RUN mkdir /etc/nginx/sites-enabled
RUN mkdir /etc/nginx/sites-available/
RUN mkdir /etc/nginx/snippets/

COPY nginx.conf /etc/nginx/nginx.conf
#COPY my_nginx_ssl.conf /etc/nginx/sites-available/
COPY ssl-params.conf /etc/nginx/snippets/
COPY ssl-www.good-roader.tk.conf /etc/nginx/snippets/

RUN ln -s /etc/nginx/sites-available/my_nginx_ssl.conf /etc/nginx/sites-enabled/

CMD ["nginx", "-g", "daemon off;"]