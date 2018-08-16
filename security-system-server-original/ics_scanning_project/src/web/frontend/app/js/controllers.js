/**
 * Created by WangAo on 2017/5/12.
 */

searchModule.controller("searchInitCtrl", ['$scope', '$element', '$interval', '$timeout', '$state', '$stateParams', 'httpService', "inputService",
    function ($scope, $element, $interval, $timeout, $state, $stateParams, httpService, inputService) {
        $scope.input = Object.create(inputService.input);
        $scope.input.keyOnClick = function (key) {
            $scope.input.key = key;
            $state.go('search_result', {"searchKey": key});
        }//点击相关关键词
        $scope.input.submit =function () {
            if ($scope.input.key != "") $state.go('search_result', {"searchKey":  $scope.input.key, "searchType": $scope.input.type});
        }//提交关键字开始搜索

        $scope.protocol = {
            list: [],
            searchProtocol: function (name) {
                $state.go('search_result', {
                    "searchKey": "protocol: "+name,
                    "searchType": "host",
                    "currentPage": "1"
                });
            },
            searchPort: function (value) {
                $state.go('search_result', {
                    "searchKey": "port: "+value,
                    "searchType": "host",
                    "currentPage": "1"
                });
            }
        }
        
        $scope.refreshContent = function () {
            httpService
                .getProtocols()
                .success(function (result, status) {
                    $scope.$apply(function () {
                       $scope.protocol.list = result.protocols;
                    }, 100);
                })
                .error(function (result, status) {
                })
        };

        $scope.refreshContent();
        
        $scope.$watch("input.key", function (newVal, oldVal, scope) {
            if (newVal != oldVal) {
                if (scope.waitKeyUp)    $timeout.cancel(scope.waitKeyUp);
                scope.waitKeyUp = $timeout(function () {
                    scope.$apply(function () {
                        if (newVal != "")   scope.input.related = true;
                        else    scope.input.related = false;
                    })
                }, 300);
            }
        });
}])

searchModule.controller("searchResultCtrl", ['$scope', '$element', '$interval', '$timeout', '$state', '$stateParams', 'httpService', "inputService",
    function ($scope, $element, $interval, $timeout, $state, $stateParams, httpService, inputService) {
        $scope.input = Object.create(inputService.input);
        $scope.input.key = $stateParams.searchKey;
        if ($stateParams.searchType != "") {
            $scope.input.type = $stateParams.searchType;
        }
        $scope.input.submit = function (e) {
            $state.go('search_result', {
                "searchKey": $scope.input.key,
                "searchType": $scope.input.type,
                "currentPage": "1"
            });
            e.preventDefault();
        }

        $scope.result = {
            timeCost: 0,
            list: [],
            totalNum: 0,
            totalPage: 0,
            currentPage: 1,
            indexNum: 9,//结果显示的页码个数
            pageList: [1, 2, 3, 4, 5, 6, 7, 8, 9],
            getPageList: function (total, current) {
                this.pageList = [];
                var start = current - parseInt(this.indexNum/2);
                var end = current + parseInt(this.indexNum/2);
                if (start < 1)  start = 1;
                if (end > total)    end = total;
                for (var i = start ; i <= end ; i++)    this.pageList.push(i);
            },
            setPage: function (v) {
                this.currentPage = v;
                $state.go('search_result', {
                    "searchKey": $scope.input.key,
                    "searchType": $scope.input.type,
                    "currentPage": this.currentPage
                });
            }
        }

        if ($stateParams.currentPage != "") {
            $scope.result.currentPage = $stateParams.currentPage;
        }

        $scope.refreshContent = function () {
            if ($scope.input.key != "") {
                var start = new Date();
                httpService
                    .getSearchResult($scope.input.key, $scope.input.type, $scope.result.currentPage)
                    .success(function (result, status) {
                        console.log(result.result);
                        var end = new Date();
                        $scope.$apply(function () {
                            $scope.result.timeCost = end.getTime()-start.getTime();
                            $scope.result.list = [];
                            $scope.result.list = result.result;
                            $scope.result.totalNum = result.tn;
                            $scope.result.totalPage = result.tp;
                            $scope.result.currentPage = result.p;
                            $scope.result.getPageList(result.tp, result.p);
                            $scope.input.related = false;
                        })
                    })
                    .error(function (result, status) {
                        
                    })
            }
        }

        $scope.refreshContent();
        
        $scope.$watch("input.key", function (newVal, oldVal, scope) {
            if (newVal != oldVal) {
                if (scope.waitKeyUp)    $timeout.cancel(scope.waitKeyUp);
                scope.waitKeyUp = $timeout(function () {
                    scope.$apply(function () {
                        if (newVal != "")   scope.input.related = true;
                        else    scope.input.related = false;
                    })
                }, 300);
            }
        });
    }])