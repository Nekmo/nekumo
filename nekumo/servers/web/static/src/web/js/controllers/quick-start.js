/**
 * Created by nekmo on 25/03/16.
 */
app.controller('quickStart', function($scope, Node){
    var quickStart = Node.create('.nekumo/quick-start');

    $scope.availabilityOptions = [
        {name: 'Sólo este equipo', id: 'this_device'},
        {name: 'Red de casa', id: 'home_network'},
        {name: 'Todo internet', id: 'internet'}
    ];
    $scope.adminAvailabilityOptions = [
        {name: 'Para este equipo', id: 'this_device'},
        {name: 'En red de casa', id: 'home_network'},
        {name: 'Requiere login', id: 'login'}
    ];
    $scope.anonymousPermsOptions = [
        {name: 'Ningún permiso', id: 'none'},
        {name: 'Sólo lectura', id: 'read'},
        {name: 'Sólo escritura', id: 'write'},
        {name: 'Lectura y escritura', id: 'read_write'}
    ];
    $scope.data = {};
    //$scope.data.availability = $scope.availabilityOptions[0]['id'];
    //$scope.data.adminAvailability = $scope.adminAvailabilityOptions[0]['id'];
    //$scope.data.anonymousPerms = $scope.anonymousPermsOptions[3]['id'];
    //$scope.data.address = '127.0.0.1';
    //$scope.data.port = 7700;
    $scope.isChanged = false;

    $scope.fieldChange = function(section){
        $scope.isChanged = true;
    };

    $scope.save = function(){
        quickStart.execute('write', {"data": $scope.data}, function(data){
            $scope.data = data.data;
        });
    };

    $scope.loadData = function() {
        quickStart.execute('read', function(data){
            $scope.data = data.data;
        });
    };

    $scope.hideQuickStart = function(){
        quickStart.execute('show_quickstart', {'value': false});
        $scope.Nodes.showQuickAdmin = false;
    };
    $scope.loadData();
});