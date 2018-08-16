#!/bin/bash

cd "/usr/local/security-system-server/data_import/"
python knowledgeBaseTest.py

db="/usr/local/security-system-server/security_system/db.sqlite3"
cd "data/knowledgeBaseSQL"

sqlite3 ${db} '.bail OFF';
sqlite3 ${db} 'delete from knowledgeBase_protocol';
sqlite3 ${db} '.import protocol.csv knowledgeBase_protocol';
sqlite3 ${db} 'delete from knowledgeBase_devicetype';
sqlite3 ${db} '.import deviceType.csv knowledgeBase_devicetype';
sqlite3 ${db} 'delete from knowledgeBase_device';
sqlite3 ${db} '.import device.csv knowledgeBase_device';
sqlite3 ${db} 'delete from knowledgeBase_instance';
sqlite3 ${db} '.import instance.csv knowledgeBase_instance';
sqlite3 ${db} 'delete from knowledgeBase_vendor';
sqlite3 ${db} '.import vendor.csv knowledgeBase_vendor';
sqlite3 ${db} 'delete from knowledgeBase_event';
sqlite3 ${db} '.import event.csv knowledgeBase_event';
sqlite3 ${db} 'delete from knowledgeBase_vulnerability';
sqlite3 ${db} '.import vulnerability.csv knowledgeBase_vulnerability';
sqlite3 ${db} 'VACUUM db';
