from django.conf.urls import url

from knowledgeBase import views as knowledgeBase
from queryAPI import views

urlpatterns = [
    url(r'^api/get/node/(id)/(\d+)/$', views.getNode),
    url(r'^api/get/node/(name)/(.+)/$', views.getNode),

    url(r'^api/get/neighborhoods/(id)/(\d+)/$', views.getNeigh),
    url(r'^api/get/neighborhoods/$', views.getNeighborhoods),
    url(r'^api/get/neighborhoodsType/id/(\d+)/$', views.getNeighborType),

    url(r'^api/get/edge/(.+)/(.+)/$', views.getEdge),

    url(r'^api/get/commonAdjacent/$', views.commonAdjacent),

    url(r'^api/post/addNode/$', views.addNode),
    url(r'^api/post/addEdge/$', views.addEdge),

    url(r'^api/post/dropNode/id/(\d+)/$', views.dropNode),
    url(r'^api/post/dropEdge/id/(.+)/$', views.dropEdge),

    url(r'^api/get/groupCount/(.+)/$', knowledgeBase.groupCount),
    url(r'^api/get/instance/$', knowledgeBase.getInstance),
    url(r'^api/get/vulnerability/$', knowledgeBase.getVulnerability),
    url(r'^api/protocols$', knowledgeBase.get_protocols),
    url(r'^api/search$', knowledgeBase.search),
    url(r'^api/post/switchGraph/(.+)/$', views.switchGraph),

    url(r'^api/get/Sex/$', views.getSex),
    url(r'^api/get/Place/$', views.getPlace),
    url(r'^api/get/Line/$', views.getLine),
    url(r'^api/get/Line/(.+)/$', views.getLine),
    url(r'^api/get/Fans/$', views.getFans),
    url(r'^api/get/Fans/(.+)/$', views.getFans),
    url(r'^api/get/Repost/$', views.getRepost),
    url(r'^api/get/Repost/(.+)/$', views.getRepost),
    url(r'^api/get/Index/$', views.getIndex),
    url(r'^api/get/Weibo/$', views.getWeibo),
    url(r'^api/get/News/(.*)/$', views.getNews),
    url(r'^api/get/Scadablog/$', views.getScadablog),
    url(r'^api/get/Scadanews/$', views.getScadanews),
    url(r'^api/get/AttackMap/$', views.getAttackMap),
    url(r'^api/get/Attacker/$', views.getAttacker),
    url(r'^api/get/Target/$', views.getTarget),
    url(r'^api/get/Type/$', views.getType),
    url(r'^api/get/VulIndex/$', views.getVulIndex),
    url(r'^api/get/ThreatenIndex/$', views.getThreatenIndex),
    url(r'^api/get/SecurityIndex/$', views.getSecurityIndex),
    url(r'^api/get/Statistics/$', views.getStatistics),
    url(r'^api/get/Paper/$', views.getPaper),
    url(r'^api/get/SegPaper/(.*)/(.*)/$', views.getSegPaper),
    url(r'^api/get/Shop/$', views.getShop),
    url(r'^api/get/SegShop/(.*)/(.*)/(.*)/$', views.getSegShop),
    url(r'^api/get/Cve/$', views.getCve),
    url(r'^api/get/SegCve/(.*)/(.*)/$', views.getSegCve),
    url(r'^api/get/Ips/$', views.getIps),
    url(r'^api/get/SegIps/(.*)/(.*)/$', views.getSegIps),
    url(r'^api/get/CountYears/$', views.countYears),
    url(r'^api/get/Cvelevel/$', views.countCveLevel),
    url(r'^api/get/CNContent/(.*)/(.*)/$', views.getCNContent),
    url(r'^api/get/ENContent/(.*)/(.*)/$', views.getENContent),
    url(r'^api/get/WeiboInfo/$', views.getweiboInfo),
    ################################### update on 2016.12.14 #################################
    url(r'^api/get/ENBlog/(.*)/(.*)/$', views.getENBlog),
    url(r'^api/get/CNBlog/(.*)/(.*)/$', views.getCNBlog),

    ################################### update on 2017.01.10 #################################
    url(r'^api/get/Malware/(.*)/(.*)/$', views.getMalware),

    url(r'^api/get/Conpots/$', views.getConpots),
    url(r'^api/get/Conpots_info/(.*)/(.*)/$', views.get_Conpots2),
    url(r'^api/get/AttackerCountry/$', views.getAttackerCountry),
    url(r'^api/get/TargetCountry/$', views.getTargetCountry),
    url(r'^api/get/TimeSequence/$', views.getTimeSequence),
    url(r'^api/get/ThreatCrowd/(.*)/(.*)/$', views.getThreatCrowd),
    url(r'^api/get/IPInfo/(.*)/$', views.getIPInfo),
    ################################### update on 2017.01.13 by Xiaosong #################################
    url(r'^api/get/DDos/$', views.eventsDDos),
    url(r'^api/get/German/$', views.eventsGerman),
    url(r'^api/get/Ukraine/$', views.eventsUkr),
    url(r'^api/get/Stuxnet/$', views.eventsStuxnet),
    ###################################update on 2017.01.15#####################################
    url(r'^api/get/WeiboHeat/(.*)/$', views.getWeiboHeat),
    url(r'^api/get/IpStatistic/$', views.getIpStatistic),
    url(r'^api/get/IpsForThreat/$', views.getIpsForThreat),
    url(r'^api/get/AttackNum/$', views.getAttackNum),
    url(r'^api/get/Conpots_info_ics/(.*)/(.*)/$', views.getConpots_info_ics),
    url(r'^api/get/QuantityOfEachSource/$', views.getQuantityOfEachSource),
    ################################## update on 2017.01.16 by lizihan #####################################
    url(r'^api/get/PageNum/(.*)/(.*)/$', views.getPageNum),
    url(r'^api/get/BlogsAndNews/(.*)/(.*)/(.*)/$', views.getBlogAndNews),
    url(r'^api/get/BlogsAndNews4Page/(.*)/(.*)/(.*)/(.*)/$', views.getBlogAndNews4Page),
    url(r'^api/get/SearchCve/(.*)/$', views.getSearchCve),
    url(r'^api/get/AllIndex/$', views.getAllIndex),
    ################################## update on 2017.05.23 by Xiaosong #####################################
    # url(r'^api/get/multichannel/(.*)/$', views.multichannel),

    url(r'^api/syn/cve/$', views.syn_cve),
    url(r'^api/syn/conpotlog/$', views.syn_conpot_log),
    url(r'^api/syn/geoinfo/$', views.syn_geo_info),
    url(r'^api/syn/geoinfotarget/$', views.syn_geo_info_target),
    url(r'^api/syn/geoinfoorg/$', views.syn_geo_info_org),
    url(r'^api/syn/geoinfotargetorg/$', views.syn_geo_info_target_org),
]
