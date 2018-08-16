/**
 * Created by WangAo on 2017/5/13.
 */

systemModule.constant("SETTINGS", {
    //backendAddress: "/api"
    backendAddress: "/api"
});

systemModule.factory("httpService", ["$http", "SETTINGS",
    function ($http, SETTINGS) {
        return {
            settings: {
                backendAddress: SETTINGS.backendAddress
            },
            getProtocols: function () {
                return $.get(this.settings.backendAddress + '/protocols');
            },
            getSearchResult: function (searchKey, searchType, pageNum) {
                var args = {
                    t: searchType,
                    q: searchKey,
                    p: pageNum
                }
                return $.get(this.settings.backendAddress + '/search', args);
            },
        }
    }
])

systemModule.service("inputService", function () {
    this.input = {
        key: "",//搜索关键词
        type: "host",//搜索类型
        options: [
            {name: "设备", value: "host"},
            {name: "网站", value: "web"},
        ],
        waitKeyUp: null,//等待离开键盘的定时器

        related: false,//是否显示相关关键词
        relatedKey: [],//相关关键词

        closeRelated: function () {
            this.related = false;
        },//关闭相关关键词
        keyOnClick: function (key) {
        },//点击相关关键词
        submit: function () {
        }//提交关键字开始搜索
    };
})
