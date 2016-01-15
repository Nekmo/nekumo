
function getCurrentNode(){
    return document.location.pathname;
}

app.controller('BaseCtrl', function($rootScope, $scope, $mdMenu){
    $mdMenu._hide = $mdMenu.hide;
    $mdMenu.hide = function(){
        $rootScope.$broadcast('mdMenuHidden');
        $mdMenu._hide.apply(this, arguments);
    };
});