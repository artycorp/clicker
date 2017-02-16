# Clicker
search some text on yandex and calculate its position.

##Install
*open terminal
 sudo crontab -e
*add this line and save
⋅⋅⋅* */1 * * *	export DISPLAY=:0.0 && cd /home/den/clicker && python main.py >> /var/log/test.log
*sudo service cron restart