/**
 * Created by nekmo on 25/03/16.
 */
app.directive('fileViewer', function($sce, $ocLazyLoad, $compile, $http, $window){
    return {
        scope: {
            node: '='
        },
        templateUrl: '/.nekumo/static/src/web/templates/file-viewer.tmpl.html',
        link: function (scope, elem) {

            var moduleGroup = null;
            var mimetype = scope.node.mimetype || '';
            scope.viewer = MIMETYPES_VIEWERS[mimetype];
            if(!scope.viewer) {
                var type = mimetype.split('/')[0];
                scope.viewer = MIMETYPES_VIEWERS[type];
            }
            if(scope.viewer == 'video') {
                //$ocLazyLoad.load('Videogular').then(function () {
                //    $compile(elem.children())(scope);
                //});
                moduleGroup = 'Videogular';

                scope.config = {
                    sources: [
                        {src: $sce.trustAsResourceUrl(scope.node.node), type: scope.node.mimetype}
                        //{src: $sce.trustAsResourceUrl("http://static.videogular.com/assets/videos/videogular.mp4"), type: "video/mp4"},
                        //{src: $sce.trustAsResourceUrl("http://static.videogular.com/assets/videos/videogular.webm"), type: "video/webm"},
                        //{src: $sce.trustAsResourceUrl("http://static.videogular.com/assets/videos/videogular.ogg"), type: "video/ogg"}
                    ],
                    //tracks: [
                    //    {
                    //        src: "http://www.videogular.com/assets/subs/pale-blue-dot.vtt",
                    //        kind: "subtitles",
                    //        srclang: "en",
                    //        label: "English",
                    //        default: ""
                    //    }
                    //],
                    theme: "/static/src/web/libs/videogular-themes-default/videogular.css",
                    plugins: {
                        controls: {
                            autoHide: true,
                            autoHideTime: 5000
                        }
                        //poster: "http://www.videogular.com/assets/images/videogular.png"
                    }
                };
            } else if(scope.viewer == 'image'){
                scope.src = scope.node;
            } else if(scope.viewer == 'text'){
                $http.get(scope.node.node).then(function(response){
                    scope.text = response.data;

                    $ocLazyLoad.load('Ace').then(function () {
                        $compile(elem.children())(scope);
                    });
                });
            }
            if(moduleGroup){
                $ocLazyLoad.load(moduleGroup).then(function () {
                    $compile(elem.children())(scope);
                });
            }

            scope.download = function(){
                $window.open(scope.node.node, '_blank');
            }
        }
    }
});
