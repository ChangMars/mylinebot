FROM nginx:latest

RUN mkdir /etc/nginx/sites-enabled
RUN mkdir /etc/nginx/sites-available/
RUN mkdir /etc/nginx/snippets/

COPY nginx.conf /etc/nginx/nginx.conf
COPY default_nginx.conf /etc/nginx/sites-available/
COPY ssl-params.conf /etc/nginx/snippets/
COPY ssl-www.good-road-bot.ga.conf /etc/nginx/snippets/
COPY dhparam.pem /etc/ssl/certs/

RUN ln -s /etc/nginx/sites-available/default_nginx.conf /etc/nginx/sites-enabled/

CMD ["nginx", "-g", "daemon off;"]