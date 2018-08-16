开发说明
====

## 项目初始化
```
django-admin startproject icsscan
```
此命令用于生成最初的Django代码，所以所有开发者只执行一次，不用再次执行。
所以可以跳过此步骤.

## 安装所需软件

1. 安装Python
1. 安装Django
1. 安装MySQL数据库
1. 安装MySQL的python驱动

## 建立数据库
```sql
create database ics_scanning character set utf8;
```

## 导入现有数据库
导入SQL目录下的数据库备份文件:
```sql
mysql -uroot -p ics_scanning < /path/backupfile.sql 
```


## 建立模块
当前项目只有一个模块home，整个项目功能还比较少，所以暂不设置其他模块。所以此步骤可以跳过。
```cmd
python manage.py startapp <name>
```

通过数据库现有的表结构生成模型命令 (此步骤不用执行)：
```cmd
python manage.py inspectdb > models.py
```

## 建立超级管理员
```cmd
python manage.py createsuperuser
```
用户名一般为admin。
建立完成通过浏览器访问http://localhost:8000/admin/来管理表数据。

