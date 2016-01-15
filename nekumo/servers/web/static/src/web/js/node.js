

var ICONS = {
    'inode/directory': {'icon': 'folder', 'color': '#17b5f9'},
    'text': {'icon': 'description', 'color': '#de3641'},
    'video': {'icon': 'movie', 'color': '#004d40'},
    'audio/ogg': {'icon': 'file-formats-icons-ogg'},
    'image/jpeg': {'icon': 'file-formats-icons-jpg3'},
    'image/png': {'icon': 'file-formats-icons-png3'},
    'application/zip': {'icon': 'file-formats-icons-zip6'},
    'audio/mpeg': {'icon': 'file-formats-icons-mp36'},
    'application/x-javascript': {'icon': 'file-formats-icons-js2'},
    'text/x-python': {'icon': 'file-formats-icons-python3'},
    'application/pdf': {'icon': 'file-formats-icons-pdf19'},
    'application/x-rar-compressed': {'icon': 'file-formats-icons-rar2'},
    'application/x-bittorrent': {'icon': 'file-formats-icons-torrent'},
    'text/css': {'icon': 'file-formats-icons-css5'},
    'text/html': {'icon': 'file-formats-icons-html9'},
    null: {'icon': 'help', 'style': 'padding-left: 2px;'}
};

function ProgrammingError(message) {
   this.message = message;
   this.name = "ProgrammingError";
}


function absolute(base, relative) {
    if(relative == '/'){
        return '/';
    }
    var stack = base.split("/"),
        parts = relative.split("/");
    stack.pop(); // remove current file name (or empty string)
                 // (omit if "base" is the current folder without trailing slash)
    for (var i=0; i<parts.length; i++) {
        if (parts[i] == ".")
            continue;
        if (parts[i] == "..")
            stack.pop();
        else
            stack.push(parts[i]);
    }
    return stack.join("/");
}


function humanize_count_nodes(files, dirs) {
    files = (Number.isInteger(files) ? files : files.length);
    dirs = (Number.isInteger(dirs) ? dirs : dirs.length);
    var msg = '';
    msg += (files ? sprintf('%d archivo%s', files, (files > 1 ? 's' : '')) : '');
    msg += (files && dirs ? ' y ' : '');
    msg += (dirs ? sprintf('%d carpeta%s', dirs, (dirs > 1 ? 's' : '')) : '');
    return msg;
}


app.config(function(NotificationProvider, $locationProvider) {
    NotificationProvider.setOptions({
        delay: 30000,
        startTop: 10,
        startRight: 10,
        verticalSpacing: 20,
        horizontalSpacing: 20,
        positionX: 'right',
        positionY: 'bottom'
    });
    // use the HTML5 History API
    $locationProvider.html5Mode({enabled: true, requireBase: false});
});

app.config(function ($mdThemingProvider) {

    $mdThemingProvider
        .theme('default')
        .primaryPalette('indigo')
        .accentPalette('blue')
        .warnPalette('red');
        // .backgroundPalette('background')
});


app.factory('Node', function(WebSocket){
    var NodeObject = function(data, nodes){
        var self = this;
        self.selected = false;
        // TODO: nodes. $scope de Nodes

        self.__init__ = function(){
            self.node = self.get_node();
        };

        $.each(data, function(key, value){
            self[key] = value;
        });

        self.get_relative_path = function(){
            if(self.type == 'dir'){
                return self.name + '/';
            }
            return self.name;
        };

        self.get_node = function(){
            var node = decodeURIComponent(self['node']);
            if(node[0] != '/'){
                node = '/' + node;
            }
            return node;
        };

        self.get_subnode = function(subnode){
            var node = self.get_node();
            if(!_.endsWith(node, '/')){
                node += '/';
            }
            node += subnode;
            node = new NodeObject({node: node, name: subnode});
            return node;
        };

        self.split = function(){
            var nodes_split = self.get_node().split('/');
            var last = nodes_split.pop();
            var new_node = new NodeObject({node: nodes_split.join('/'), name: nodes_split[nodes_split.length - 1],
                                           type: 'dir'});
            return [new_node, last];
        };

        self.copy = function(dest, success, error, complete){
            WebSocket.get({'method': 'copy', 'node': self.get_node(), 'dest': dest.get_node(), 'override': true})
                .then(success, error, complete);
        };

        self.exists = function(success, error, complete){
            WebSocket.get({'method': 'exists', 'node': self.get_node()})
                .then(success, error, complete);
        };

        self.move = function(dest, success, error, complete){
            WebSocket.get({'method': 'move', 'node': self.get_node(), 'dest': dest.get_node(), 'override': true})
                .then(success, error, complete);
        };

        self.count = function(success, error, complete){
            if(self['type'] != 'dir'){
                throw new ProgrammingError('Count solo se puede usar en directorios.');
            }
            WebSocket.get({'method': 'count', 'node': self.get_node()}).then(success, error, complete);
        };

        self.rm = function(success, error, complete){
            WebSocket.get({'method': 'rm', 'node': self.get_node()}).then(success, error, complete);
        };

        self.get_icon = function(){
            var mimetype = self['mimetype'];
            var icon = ICONS[mimetype];
            if(icon == undefined) {
                mimetype = mimetype.split('/')[0];
                icon = ICONS[mimetype];
            }
            if(icon == undefined){
                return ICONS[null]
            }
            return icon;
        };

        self.select = function(){
            self.selected = true;
            if(nodes.selected.indexOf(self) == -1){
                nodes.selected.push(self);
            }
        };

        self.unselect = function(){
            self.selected = false;
            if(nodes.selected.indexOf(self) > -1){
                nodes.selected.splice(nodes.selected.indexOf(self), 1);
            }
        };

        self.isSelected = function(){
            return self.selected;
        };

        self.toggleSelect = function(){
            if(self.isSelected()){
                self.unselect();
            } else {
                self.select();
            }
        };

        self.__init__();
    };
    NodeObject.prototype.constructor = Object;


    return {
        create: function(data, nodes){
            return new NodeObject(data, nodes);
        }
    }
});


app.filter('decodeURIComponent', function() {
    return window.decodeURIComponent;
});


app.filter('bytes', function() {
    return function(bytes, precision) {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) return '-';
        if(bytes == 0){ return '0 bytes'}
        if (typeof precision === 'undefined') precision = 1;
        var units = ['bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'],
            number = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, Math.floor(number))).toFixed(precision) +  ' ' + units[number];
    }
});


app.animation('.ani-slide', [function($timeout) {
  return {
    // make note that other events (like addClass/removeClass)
    // have different function input parameters
    enter: function(element, doneFn) {
        jQuery(element).fadeIn(1000, doneFn);

      // remember to call doneFn so that angular
      // knows that the animation has concluded
    },

    move: function(element, doneFn) {
        jQuery(element).fadeIn(1000, doneFn);
    },

    leave: function(element, doneFn) {
        // TODO: El fondo no está funcionando
        jQuery(element).addClass('alert');
        setTimeout(function(){
            jQuery(element).fadeOut(1000, doneFn);
        }, 1500);
    }
  }
}]);

app.directive('nekumoNodeMenu', function($rootScope, $timeout){
    return {
        scope: {
            node: '='
        },
        templateUrl: 'nekumo/menu-node.tmpl.html',
        link: function(scope){
            scope.open_menu = function($mdOpenMenu, ev) {
                // TODO: menu_right
                if(scope.node && !(scope.node.selected)){
                    scope.node.select();
                    scope.menu_right_node = scope.node;
                }
                $mdOpenMenu(ev);

                $rootScope.$on('mdMenuHidden', function(){
                    $timeout(function(){
                        // El evento de cerrar menú se lanza antes que la ejecución de los métodos del propio menú,
                        // por lo que no hay forma de diferenciar cuando se ha pulsado una opción, o se ha cerrado
                        // el menú por tocar otra parte de la pantalla. Por ello, pongo un timeout, para que dé
                        // tiempo a que se inicie la ejecución del método seleccionado en el menú.
                        // TODO:
                        if($scope.menu_right_node == null){
                            return
                        }
                        console.debug('Deseleccionar ' + $scope.menu_right_node);
                        $scope.menu_right_node.unselect();
                        $scope.menu_right_node = null;
                    }, 50);
                });
            };

            scope.menuCtrl = {
                paste: scope.$parent.paste,
                copy: scope.$parent.copy,
                cut: scope.$parent.cut,
                rm: scope.$parent.rm
            };
        }
    }
});

app.controller('Nodes', function ($rootScope, $scope, $timeout, $location, $window, $mdDialog, $mdToast, $mdMenu,
                                  WebSocket, Node, DialogMessage) {
    // Debug
    NodesScope = $scope;
    $scope.filter = {};
    $scope.orderField = 'name';
    $scope.selected = [];
    $scope.cut_copy_nodes_exists = []; // Elementos que se copiarán o moverán en el pegado
    $scope.cut_copy_action = ''; // copy o move. Acción de pegado en la que se está ahora
    $scope.cutCopyDefaultAction = null;
    $scope.name = ''; // Nombre del nodo en el que se encuentra ahora
    // El nodo que se ha seleccionado por usar el menú. Si se cancela la operación, debe devolverse a su
    // estado original
    $scope.menu_right_node = null;

    var cut_copy = function(){
        var selected = $scope.get_selected_nodes();
        $scope.cut_copy_nodes = [];
        angular.forEach(selected, function(x){x.extra_style_class = 'cut_copy'; x.unselect();
            $scope.cut_copy_nodes.push(x)});
        $mdToast.show(
            $mdToast.simple()
                .action('Cancelar')
                .highlightAction(false)
                .content('Tiene archivos en su portapapeles listos para pegar.')
                .hideDelay(0)
        ).then(function(response){
            if(response == 'ok'){
                // Se ha cancelado el pegado
                angular.forEach($scope.cut_copy_nodes, function(x){ x.extra_style_class = '' });
                $scope.cut_copy_nodes = [];
                $scope.cut_copy_action = '';
                $mdToast.show(
                    $mdToast.simple()
                        .content('Se ha cancelado el pegado de los archivos.')
                );
            }
        });
    };

    $scope.getDirectory = function(node){
        // TODO: cambiar a loadDirectory
        if(!node){
            node = $scope.node;
        }
        $scope.unselectAll();
        $scope.nodes = null;
        // Añadiremos y quitaremos ani-slide debido a un bug en mdTable, que no permite usar ngClass.
        $('#nodes').find('tr').removeClass('ani-slide');

        var loading = $timeout(function(){
            $('#loading').show();
        }, 20);
        var slow_load = $timeout(function(){
            $scope.slow_load = true;
        }, 50);
        WebSocket.get({'method': 'ls', 'node': decodeURIComponent(node)}).then(function (data) {
            $scope.nodes = _.map(data.nodes, function (node) {
                return new Node.create(node, $scope);
            });
            $scope.name = data.name;
            $timeout.cancel(slow_load);
            $timeout.cancel(loading);
            $('#nodes').find('tr').addClass('ani-slide');
            $('#loading').hide();
            $scope.slow_load = false;
        }, function(data){
            DialogMessage.error('Error al listar el directorio',
                printf('Se ha producido un error al solicitar un directorio. El servidor devolvió: «%s»',
                    data.message))
        });
    };

    $scope.get_breadcrumb_nodes = function(){
        var nodes = $scope.node.split('/');
        nodes = nodes.slice(1, nodes.length - 1);
        // nodes.splice(0, 0, '');
        return nodes;
    };

    $scope.get_selected_nodes = function(){
        return _.filter($scope.nodes, function(node){ return node.selected });
    };

    $scope.toggleSelected = function(){
        if(!$scope.allSelected()){
            $scope.selectAll();
        } else {
            $scope.unselectAll();
        }
    };

    $scope.allSelected = function(){
        return $scope.selected.length >= ($scope.nodes || []).length;
    };

    $scope.selectAll = function(){
            angular.forEach($scope.nodes, function(x){x.select()})
        };

    $scope.unselectAll = function(){
        angular.forEach($scope.get_selected_nodes(), function(x){x.unselect()})
    };

    $scope.set_menu_right_node = function(node){
        $scope.menu_right_node = node;
    };

    $scope.remove_node = function(node, list){
        if(list == undefined){
            list = $scope.nodes;
        }
        _.remove(list, function(n){ return node == n.get_node() });
    };

    $scope.go_to = function(node, $event){
        node = absolute(getCurrentNode(), node);
        if($event != undefined){
            $event.preventDefault();
        }
        $location.path(node);

        $timeout(function(){
            $scope.node = getCurrentNode();
            $scope.breadcrumb_nodes = $scope.get_breadcrumb_nodes();
            $scope.getDirectory();
        }, 50);
    };

    $scope.rm = function(node, ev){
        var rm_dialog = function(dirs, files, dirs_count, files_count){
            // Mostrar un diálogo con los archivos que se borrarán, y al pulsar aceptar,
            // borrarlos definitivamente.
            var msg = 'Ha seleccionado ';
            msg += humanize_count_nodes(files, dirs) + '.';
            if(files_count || dirs_count){
                msg += sprintf(' Además, por el borrado de %s, se perderá: ',
                               (dirs.length > 1 ? 'las carpetas' : 'la carpeta'));
                // msg += humanize_count_nodes(files_count, dirs_count - dirs.length);
                msg += humanize_count_nodes(files_count, dirs_count);
                msg += '.';
            }
            // TODO: En Angular Material 0.11 soportará HTML content
            var confirm = $mdDialog.confirm()
                  .title('Peligro de manazas: borrado de archivos.')
                  .content(msg)
                  .ariaLabel('Lucky day')
                  .ok('Aceptar')
                  .cancel('Mejor no')
                  .targetEvent(ev);
            $mdDialog.show(confirm).then(function() {
                function removed_callback(data){
                    var node = data.node;
                    $scope.remove_node(node);
                }
                angular.forEach(files, function(file){ file.rm(removed_callback); });
                angular.forEach(dirs, function(dir){ dir.rm(removed_callback); });
                $scope.unselectAll();
            }, function() {
                // Cancelado.
                $scope.unselectAll();
            });
        };

        var selected = $scope.get_selected_nodes();
        var dirs = _.filter(selected, function(node){ return node.type == 'dir' });
        var files = _.filter(selected, function(node){ return node.type != 'dir' });
        var dirs_cascade_count = 0; // Borrado en cascada en cons. de borrado directorios
        var files_cascade_count = 0;
        if(!dirs.length){
            // Son solo archivos. No es necesario investigar más.
            rm_dialog(dirs, files, dirs_cascade_count, files_cascade_count);
        } else {
            var dir_count = 0;
            var complete_function = function(data){
                dirs_cascade_count += data.dirs;
                files_cascade_count += data.files;
                dir_count += 1;
                if(dirs.length > dir_count){
                    dirs[dir_count].count(complete_function);
                } else {
                    rm_dialog(dirs, files, dirs_cascade_count, files_cascade_count);
                }
            };
            dirs[dir_count].count(complete_function);
        }
    };

    $scope.cut = function(){
        $scope.cut_copy_action = 'cut';
        cut_copy();
    };

    $scope.copy = function(){
        $scope.cut_copy_action = 'copy';
        cut_copy();
    };

    $scope.paste = function(dest_dir){
        function pasteFinished(){
            if(!$scope.cut_copy_nodes.length){
                $scope.cut_copy_action = '';
                angular.forEach($scope.nodes, function(x){
                    x.extra_style_class = (x.extra_style_class ?
                        x.extra_style_class.replace('cut_copy', '') : '');
                });
                $mdToast.show(
                    $mdToast.simple()
                        .content('Todos los archivos se han terminado de pegar.')
                );
            }
        }
        function paste(orig, dest_node, action){
            orig[action](dest_node, function(data){
                if($scope.cut_copy_action == 'cut'){
                    $scope.remove_node(data.node);
                }
                $scope.remove_node(data.node, $scope.cut_copy_nodes);
                pasteFinished();
            });
        }
        function ignore(orig){
            $scope.remove_node(orig.node, $scope.cut_copy_nodes);
            pasteFinished();
        }
        function check_node_exists(orig, dest_node, action){
            dest_node.exists(function(data){
                if(!data.exists || $scope.cutCopyDefaultAction == 'override'){
                    return paste(orig, dest_node, action);
                }
                if($scope.cutCopyDefaultAction == 'ignore'){
                    return ignore(orig);
                }
                if(!$scope.cut_copy_nodes_exists.length){
                    // Abro por primera vez la ventana de Cut copy Nodes Exists
                    $mdDialog.show({
                        scope: $scope,
                        preserveScope: true,  // do not forget this if use parent scope
                        templateUrl: 'nekumo/copy_paste_nodes_exists.tmpl.html',
                        parent: angular.element(document.body),
                        clickOutsideToClose: false,
                        controller: function DialogController($scope, $mdDialog){
                            $scope.hide = function() {
                                $mdDialog.hide();
                            };
                            $scope.cancel = function() {
                                $mdDialog.cancel();
                            };
                            $scope.rename = function(orig, dest_node){
                                dest_node = dest_node.split()[0].get_subnode(dest_node.name);
                                check_node_exists(orig, dest_node, action);
                                $scope.clear(orig);
                            };
                            $scope.ignore = function(orig, dest_node){
                                ignore(orig);
                                $scope.clear(orig);
                            };
                            $scope.override = function(orig, dest_node){
                                paste(orig, dest_node, action);
                                $scope.clear(orig);
                            };
                            $scope.clear = function(orig){
                                var cut_copy_node_exists =_.filter($scope.cut_copy_nodes_exists, {orig: orig})[0];
                                _.remove($scope.cut_copy_nodes_exists, function(x){ return x == cut_copy_node_exists});
                                if(!$scope.cut_copy_nodes_exists.length){
                                    $scope.hide();
                                }
                            };
                            $scope.overrideAll = function(){
                                $scope.cutCopyDefaultAction = 'override';
                                $scope.applyAll();
                            };
                            $scope.ignoreAll = function(){
                                $scope.cutCopyDefaultAction = 'ignore';
                                $scope.applyAll();
                            };
                            $scope.applyAll = function(){
                                angular.forEach($scope.cut_copy_nodes_exists, function(x){
                                    $scope[$scope.cutCopyDefaultAction](x.orig, x.dest_node);
                                });
                            }
                        }
                    });
                }
                $scope.cut_copy_nodes_exists.push({orig: orig, dest_node: dest_node});
            });
        }
        $mdToast.hide(); // Oculto el Toast de archivos listos para pegar
        if(!dest_dir){
            dest_dir = $scope.node;
        } else {
            dest_dir.unselect();
            dest_dir = dest_dir.get_node();
        }
        var action = {'copy': 'copy', 'cut': 'move'}[$scope.cut_copy_action];
        angular.forEach($scope.cut_copy_nodes, function(orig){
            var dest_path = [dest_dir, orig.name].join('/');
            // Nodo destino. Pegaremos a este si no existe.
            var dest_node = new Node.create({'node': dest_path, 'name': orig.name});
            check_node_exists(orig, dest_node, action);
        });
    };

    $scope._ = _;
    $scope.Math = Math;

    // Obtener el directorio actual en el inicio. TODO: Mejorar esto.
    $scope.node = getCurrentNode();
    $scope.breadcrumb_nodes = $scope.get_breadcrumb_nodes();

    $scope.getDirectory();
});