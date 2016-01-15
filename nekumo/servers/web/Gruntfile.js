const fs = require('fs');

function readAsserts(file, regex){
    var text = fs.readFileSync(file, 'utf-8');
    return regex.exec(file);
}
// TODO: no funciona
console.log(readAsserts('templates/web/node.html', new RegExp('"{{ nekumo_root }}/([^"]+)\.js"', 'gi')));
module.exports = function(grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        uglify: {
            options: {
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
            },
            build: {
                src: readAsserts('templates/web/node.html', new RegExp('"{{ nekumo_root }}/([^"]+)\.js"')),
                dest: 'build/<%= pkg.name %>.min.js'
            }
        }
    });

    // Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // Default task(s).
    grunt.registerTask('default', ['uglify']);

};