const fs = require('fs');

function getMatches(string, regex, index) {
    index || (index = 1); // default to the first capturing group
    var matches = [];
    var match;
    while (match = regex.exec(string)) {
        matches.push(match[index]);
    }
    return matches;
}

function readAsserts(file, regex){
    regex = new RegExp(regex, 'gi');
    var text = fs.readFileSync(file, 'utf-8');
    var matches = getMatches(text, regex);
    console.log('Parsing asserts from *' + file + '*:');
    matches.forEach(function(x){
        console.log('  - ' + x);
    });
    return matches;
}

module.exports = function(grunt) {

    // Project configuration.
    // TODO: debo separar base.min.js y node.min.js por bibliotecas y código propio. Esto es debido por el corte
    // necesario para la configuración.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        ngAnnotate: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd HH:MM") %> */\n'
            },
            build: {
                files: [
                    {
                        src: readAsserts('templates/web/node.html', '"{{ nekumo_root' + ' }}/([^"}]+\.js)"'),
                        dest: '/tmp/_nekumoBuild/node.js'
                    },
                    {
                        src: readAsserts('templates/web/base.html', '"{{ nekumo_root }}/([^"}]+\.js)"'),
                        dest: '/tmp/_nekumoBuild/base.js'
                    }
                ]
            }
        },
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd HH:MM") %> */\n'
            },
            build: {
                files: [
                    {
                        src: '/tmp/_nekumoBuild/node.js',
                        dest: 'static/build/node.min.js'
                    },
                    {
                        src: '/tmp/_nekumoBuild/base.js',
                        dest: 'static/build/base.min.js'
                    }
                ]
            }
        },
        cssmin: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd HH:MM") %> */\n'
            },
            build: {
                files: [
                    {
                        src: readAsserts('templates/web/node.html', '"{{ nekumo_root' + ' }}/([^"}]+\.css)"'),
                        dest: 'static/build/node.min.css'
                    },
                    {
                        src: readAsserts('templates/web/base.html', '"{{ nekumo_root }}/([^"}]+\.css)"'),
                        dest: 'static/build/base.min.css'
                    }
                ]
            }
        }
    });

    // Load the plugin that provides the "grunt-ng-annotate" task.
    grunt.loadNpmTasks('grunt-ng-annotate');
    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify');
    // Load the plugin that provides the "cssmin" task.
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    // Default task(s).
    grunt.registerTask('default', ['ngAnnotate', 'uglify', 'cssmin']);

};