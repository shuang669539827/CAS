nohup  /opt/www/dts/bin/celery worker -A single_sign --loglevel=info --beat  -c1 > celery.txt & 
