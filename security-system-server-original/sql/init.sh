#cat use ics;source ics.sql; | mysql --user=root -p123456

mysql -uroot -p123456 -e "
use ics;
source /usr/local/security-system-server/sql/ics.sql; 
"
mysqlimport -uroot -p123456 --local ics attackmap.txt
mysqlimport -uroot -p123456 --local ics location.txt
mysqlimport -uroot -p123456 --local ics news.txt
mysqlimport -uroot -p123456 --local ics scadablog.txt
mysqlimport -uroot -p123456 --local ics scadanews.txt
mysqlimport -uroot -p123456 --local ics weibo.txt
