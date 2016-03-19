
function getCurrentNode(){
    return document.location.pathname;
}

function getPathWithoutFile(path){
    // Obtener una ruta sin la parte del nombre. Ejemplo: /foo/bar/spam,
    // como /foo/bar/. /foo/bar/ como /foo/bar/.
    if(path[path.length-1] != '/'){
        path = path.split('/');
        path.pop();
        path = path.join('/');
    }
    return path
}

app.controller('BaseCtrl', function($rootScope, $scope, $mdMenu){
    $mdMenu._hide = $mdMenu.hide;
    $mdMenu.hide = function(){
        $rootScope.$broadcast('mdMenuHidden');
        $mdMenu._hide.apply(this, arguments);
    };
});