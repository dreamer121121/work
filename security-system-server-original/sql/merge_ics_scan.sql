# 需求：
# 把扫描组的数据库ics_scanning与大数据平台组的数据库ics_scann合并的SQL语句
#

# 步骤:
# 首先把ics_scan中的knowledgeBase_instance表中的port数据导入到knowledgeBase_instanceport表中
# 目的是一个设备会有多个port信息，之前只支持一个设备一个port
insert into knowledgebase_instanceport(id, ip, port, protocol, banner, add_time, update_time, instance_id) select uuid(), ip, port, ins_type,  banner, timestamp, add_time, name from knowledgebase_instance;

update knowledgebase_instanceport set status = 'active';
update knowledgebase_instance set from_spider=1  where ip like '%*%';
update knowledgebase_instance set from_scan = 1 where ins_type = 'Camera'


-- # 导入ip location数据
insert into ics_scan.knowledgebase_iplocation(ip, lat, lng)
select ip_address, lat, lng from ics_scanning.t_ip_location;


-- # 导入ip subnet表数据
INSERT INTO ics_scan.knowledgebase_ipsubnet(`city`,`province`,`country`,`ip_subnet_from`,`ip_subnet_to`) select city, city, 'China', ip_subnet_from, ip_subnet_to from ics_scanning.t_ip_subnet;


-- # 导入protocol数据
insert into ics_scan.knowledgebase_protocol(proto_name, nw_proto, port)
SELECT proto_name, nw_proto, port FROM ics_scanning.t_protocol;

-- # 设备表由于可能存在相同的IP地址，所以需要使用程序来插入

alter table knowledgeBase_instance add index index_instance_ip(`ip`);

alter table ics_scan.knowledgebase_instance change add_time update_time datetime null;

-- # 给设备表和设备Port表增加外键关联
ALTER TABLE `knowledgeBase_instanceport` ADD INDEX `instance_id_name_idx` (`instance_id`);
ALTER TABLE `knowledgeBase_instanceport` ADD CONSTRAINT `instance_id_name` FOREIGN KEY (`instance_id`) REFERENCES `knowledgeBase_instance` (`name`);


-- # 去掉字段内容中的回车
UPDATE knowledgeBase_instance SET  lat = REPLACE(REPLACE(lat, CHAR(10), ''), CHAR(13), '');
UPDATE knowledgeBase_instance SET  lon = REPLACE(REPLACE(lon, CHAR(10), ''), CHAR(13), '');

update knowledgeBase_instance set city='' where city = 'None';
update knowledgeBase_instance set country='' where country = 'None';
