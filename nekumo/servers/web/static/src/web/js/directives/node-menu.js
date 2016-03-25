/**
 * Created by nekmo on 25/03/16.
 */
app.directive('nekumoNodeMenu', function($rootScope, $timeout, $mdBottomSheet){
    return {
        scope: {
            node: '='
        },
        templateUrl: '/.nekumo/static/src/web/templates/menu-node.tmpl.html',
        link: function(scope){
            scope.Nodes = scope.$parent.Nodes;

            scope.open_menu = function($mdOpenMenu, ev) {
                // TODO: menu_right
                if(scope.node && !(scope.node.selected)){
                    scope.node.select();
                    scope.$parent.menu_right_node = scope.node;
                }
                $mdOpenMenu(ev);

                $rootScope.$on('mdMenuHidden', function(){
                    $timeout(function(){
                        // El evento de cerrar menú se lanza antes que la ejecución de los métodos del propio menú,
                        // por lo que no hay forma de diferenciar cuando se ha pulsado una opción, o se ha cerrado
                        // el menú por tocar otra parte de la pantalla. Por ello, pongo un timeout, para que dé
                        // tiempo a que se inicie la ejecución del método seleccionado en el menú.
                        // TODO:
                        if(scope.$parent.menu_right_node == null){
                            return
                        }
                        console.debug('Deseleccionar ' + scope.$parent.menu_right_node);
                        scope.$parent.menu_right_node.unselect();
                        scope.$parent.menu_right_node = null;
                    }, 50);
                });
            };

            scope.openWith = function () {
                $mdBottomSheet.show({
                    templateUrl: '/.nekumo/static/src/web/templates/open-with.tmpl.html',
                    scope: scope
                });
                scope.node.execute('get_openers', function(data){
                    scope.openers = data.openers;
                });
            };

            scope.open = function(opener){
                opener = _.omitBy(opener, function(value, key){ return _.startsWith(key, '$') });
                scope.node.execute('open', {'opener': opener}, function() {

                });
            };

            scope.menuCtrl = {
                //openWith: scope.openWith,
                openWith: scope.openWith,
                open: scope.open,
                paste: scope.$parent.paste,
                copy: scope.$parent.copy,
                cut: scope.$parent.cut,
                rm: scope.$parent.rm
            };
        }
    }
});