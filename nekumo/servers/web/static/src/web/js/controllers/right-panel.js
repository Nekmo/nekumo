/**
 * Created by nekmo on 25/03/16.
 */
app.controller('RightPanelCtrl', function ($scope) {
    $scope.getMimetypeTitle = function(){
        return get_mimetype_value(MIMETYPES_TITLES, $scope._previewFile.node.mimetype);
    };

    $scope.getIcon = function(){
        return get_mimetype_value(ICONS, $scope._previewFile.node.mimetype)['xicon'];
    };

    $scope.getIconColor = function(){
        return get_mimetype_value(ICONS, $scope._previewFile.node.mimetype)['color']
    };

    $scope.getExtendedInfo = function(){
        var info = [];
        $scope._previewFile.node.extended_info(function(response){
            console.debug(response);
            angular.forEach(response.info || {}, function(value, key){
                info[key] = value;
            });
        });
        return info
    };

    $scope.$watch('_previewFile.node', function(){
        $scope.extendedInfo = $scope.getExtendedInfo();
    });
});