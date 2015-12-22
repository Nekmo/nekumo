
angular.module('mdDialogMessage', []).
    factory('DialogMessage', function($rootScope, $mdDialog, $mdToast){
    var dialog = function(title, message, reasons, solutions, buttons, template, clickOutsideToClose){
        var scope = $rootScope.$new();
        scope.title = title;
        scope.message = message;
        scope.reasons = reasons;
        scope.solutions = solutions;
        scope.buttons = buttons;
        $mdDialog.show({
            scope: scope,
            preserveScope: true,  // do not forget this if use parent scope
            templateUrl: template,
            parent: angular.element(document.body),
            clickOutsideToClose: clickOutsideToClose,
            controller: function DialogController($scope, $mdDialog){
                $scope.hide = function() {
                  $mdDialog.hide();
                };
                $scope.cancel = function() {
                  $mdDialog.cancel();
                };
                angular.forEach($scope.buttons, function(button){
                    if(typeof button.callback == 'string'){
                        button.callback = $scope[button.callback];
                    }
                });
            }
        });
    };
    var toast = function(title, message, reasons, solutions, buttons, template, hideDelay){
        var scope = $rootScope.$new();
        scope.title = title;
        scope.message = message;
        scope.reasons = reasons;
        scope.solutions = solutions;
        scope.buttons = buttons;
        $mdToast.show({
            scope: scope,
            preserveScope: true,  // do not forget this if use parent scope
            templateUrl: template,
            parent: angular.element(document.body),
            hideDelay: hideDelay,
            //clickOutsideToClose: clickOutsideToClose,
            controller: function DialogController($scope, $mdToast){
                $scope.hide = function() {
                  $mdToast.hide();
                };
                $scope.cancel = function() {
                  $mdToast.cancel();
                };
                angular.forEach($scope.buttons, function(button){
                    if(typeof button.callback == 'string'){
                        button.callback = $scope[button.callback];
                    }
                });
            }
        });
    };
    var critical = function(title, message, reasons, solutions){
        var buttons = [
            {message: 'Más tarde', callback: 'cancel'},
            {message: 'Reiniciar ventana', callback: function(){ location.reload(); }}
        ];
        dialog(title, message, reasons, solutions, buttons, 'nekumo/critical.tmpl.html', false);
    };
    var error = function(title, message, reasons, solutions){
        var buttons = [
            {message: '¡Entendido!', callback: 'cancel'}
        ];
        toast(title, message, reasons, solutions, buttons, 'nekumo/error.tmpl.html', 0);
    };
    return {
        critical: critical,
        error: error
    }
});
