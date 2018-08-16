/**
 * Created by WangAo on 2017/5/9.
 */
//主模块mainApp, 在此注入子模块
var mainApp = angular.module('mainApp', [
    'ui.router',
    'ui.grid',

    //Function-divided Modules
    'SearchModule',
    'ReportModule',
    //Service provider
    'SystemModule'
]);

mainApp.run(function($rootScope, $state, $stateParams) {
    $rootScope.$state = $state;
    $rootScope.$stateParams = $stateParams;
});

//页面路由配置
mainApp.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/search/init');
    $stateProvider
        .state('search_init', {
            url: '/search/init',
            templateUrl: 'tpls/search/main-search-init.html'
        })
        .state('search_result', {
            url: '/search/result?searchKey&&searchType&&currentPage',
            templateUrl: 'tpls/search/main-search-result.html',
            params: {"searchKey": "", 'searchType': "", 'currentPage': ""}
        });
    
});