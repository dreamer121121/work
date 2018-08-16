使用环境
1.linux操作系统
2.Nmap6.40版本（一般linux操作系统自带Nmap，请确认是否是6.40版本）
3.Mysql数据库，有“ics_scan”数据库以及“knowledgeBase_instance”和“knowledgeBase_instanceport”这两个表
4.数据库账号root，密码为8571512411
5.内存大于8G，CPU核心数越多越好。最好与阿里云114配置一致
7.具有python2和python3，并且命令行“python”可调用python2程序，“python3”可调用python3程序

使用方法
1.将整个目录拷贝在服务器上，拷贝后切勿修改目录下任何文件或者文件夹
2.将本文件夹下DispathAll.py放入调度任务中，每隔15天运行一次；或者不断运行DispathAll.py，即等其结束后再次运行，已达到实时探测效果

联系方式
email: liuqy@act.buaa.edu.cn