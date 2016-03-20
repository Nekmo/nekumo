

var MINIFY = {
    'videogular': [
        {'src': 'static/src/web/libs/videogular'},
        {'src': 'static/src/web/libs/videogular-controls'},
        {'src': 'static/src/web/libs/videogular-themes-default', 'types': ['css']}
    ]
};


function getMinifyObjects(minify, type){
    var group;
    var source;
    var sources;
    var results = [];
    for(group_name in minify){
        group = minify[group_name];
        sources = [];
        for(i in group){
            source = group[i];
            if(source.types && source.types.indexOf(type) == -1){
                continue
            }
            sources.push(source.src + '/**/*.min.' + type);
        }
        results.push({
            'src': sources,
            'dest': 'static/build/' + group_name + '.min.' + type
        });
    }
    return results
}

getMinifyObjects(MINIFY, 'js');

function extendsList(a, b){
    Array.prototype.push.apply(a, b);
    return a;
}

module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        // Los archivos .html tienen en las rutas el {{ nekumo_root }} en su src. Es necesario
        // retirarlo y hacerlo relativo para que usemin pueda encontrarlo y usarlo.
        // El destino será un directorio temporal llamado _tmpBuild
        replace: {
            html: {
                src: ['templates/*/*.html'],             // source files array (supports minimatch)
                dest: '_tmpBuild/',             // destination directory or file
                replacements: [{
                    from: '{{ nekumo_root }}/',                   // string replacement
                    to: '../'
                }]
            },
            css: {
                src: ['.tmp/concat/*.css'],             // source files array (supports minimatch)
                // dest: '.tmp/contat/',             // destination directory or file
                overwrite: true,
                replacements: [{
                    from: '../fonts/',                   // string replacement
                    to: ''
                }]
            },
            videogular: {
                src: ['static/build/videogular.min.css'],
                overwrite: true,
                replacements: [{
                    from: 'fonts/',
                    'to': ''
                }]
            }
        },
        // Se obtendrán todos los css y js de los html generados anteriormente y se llevarán concatenados
        // al directorio temporal .tmp/concat/
        useminPrepare: {
            html: '_tmpBuild/*.html',
            options: {
              dest: 'static/build'
            }
        },
        // A los .js se les aplica ngAnnotate para arreglar el problema con los function($scope, ...).
        ngAnnotate: {
            build: {
                files: [
                    {
                        expand: true,
                        src: '.tmp/concat/*.js'
                    }
                ]
            }
        },
        // Ahora se minifican al directorio correcto, static/build.
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd HH:MM") %> */\n'
            },
            build: {
                files: extendsList([
                    {
                        expand: true,
                        src: '.tmp/concat/*.js',
                        dest: 'static/build/'
                    }
                ],getMinifyObjects(MINIFY, 'js'))
            }
        },
        //Los CSS desde .tmp/concat/ se minifican y se llevan al directorio static/build/
        cssmin: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd HH:MM") %> */\n'
            },
            build: {
                files: [
                    extendsList([{
                        expand: true,
                        src: '.tmp/concat/*.css',
                        dest: 'static/build/'
                    }], getMinifyObjects(MINIFY, 'css'))
                ]
            }
        },
        copy: {
            fonts: {
                files: [
                    {
                        flatten: true, expand: true, src: [
                            'static/src/web/libs/mdi/fonts/*'
                        ], dest: 'static/build/'
                    },
                    {
                        flatten: true, expand: true, src: [
                            'static/src/web/libs/videogular-themes-default/fonts/*'
                        ], dest: 'static/build/'
                    }
                ]
            }
        },
        // Se borra el directorio .tmp creado por concat, _tmpBuild creado por nosotros, y
        // static/build/.tmp usado por uglify.
        clean: {
            build: ['.tmp', '_tmpBuild', 'static/build/.tmp']
        }
    });

    // Load the plugin that provides the "grunt-contrib-concat" task.
    grunt.loadNpmTasks('grunt-contrib-concat');
    // Load the plugin that provides the "grunt-text-replace" task.
    grunt.loadNpmTasks('grunt-text-replace');
    // Load the plugin that provides the "grunt-usemin" task.
    grunt.loadNpmTasks('grunt-usemin');
    // Load the plugin that provides the "grunt-ng-annotate" task.
    grunt.loadNpmTasks('grunt-ng-annotate');
    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    // Load the plugin that provides the "cssmin" task.
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    // Load the plugin that provides the "copy" task.
    grunt.loadNpmTasks('grunt-contrib-copy');
    // Load the plugin that provides the "clean" task.
    grunt.loadNpmTasks('grunt-contrib-clean');

    // Default task(s).
    grunt.registerTask('default', [
        'replace:html', 'useminPrepare', 'concat', 'ngAnnotate', 'uglify', 'replace:css',
        'cssmin', 'replace:videogular', 'copy',  'clean'
    ]);

};