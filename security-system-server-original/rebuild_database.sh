#!/bin/bash
user=root
echo "kill cassandra..."
pgrep -u $user -f cassandra | xargs kill -9

echo "kill elasticsearch..."
pgrep -u $user -f elasticsearch | xargs kill -9

#echo "kill gremlin-server..."
#pgrep -u $user -f gremlin-server | xargs kill -9

echo "remove data & logs..."
rm -r /usr/local/apache-cassandra-2.1.14/data
rm -r /usr/local/apache-cassandra-2.1.14/logs
rm -r /usr/local/elasticsearch-1.5.2/data
rm -r /usr/local/elasticsearch-1.5.2/logs

echo "start cassandra..."
nohup /usr/local/apache-cassandra-2.1.14/bin/cassandra &
sleep 8

echo "start elasticsearch..."
nohup /usr/local/elasticsearch-1.5.2/bin/elasticsearch &
sleep 5


echo "success"
