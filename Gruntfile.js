module.exports = function (grunt) {
  require('time-grunt')(grunt);
  require('jit-grunt')(grunt);
  var sassOutputStyle = grunt.option('output_style') || 'expanded';
  var bluebottlePath = grunt.option('bb_path') || ["../bluebottle/bluebottle/common/static/sass"];
  var bluebottleRefactorPath = grunt.option('bb_ref_path') || ["../bluebottle/bluebottle/common/static/refactor-sass"];

  grunt.loadNpmTasks('grunt-bower-task'); 

  // Project configuration.
  grunt.initConfig({
    sass: {
      dist: {
        options: {
          loadPath: bluebottleRefactorPath
        },
        files: [{
          expand: true,
          cwd: 'static/global/refactor-sass/',
          src: 'screen-refactor.scss',
          dest: 'static/global/css/',
          ext: '.css'
        }]
      }
    },
    pkg: grunt.file.readJSON('package.json'),
    watch: {
      options: {
        livereload: true,
      },
      sass: {
        files: ['static/global/refactor-sass/**/*', bluebottleRefactorPath+"/**/*"],
        tasks: ['sassRender:dist']
      },
      scss: {
        options: {
          livereload: false,
        },
        files: ['static/global/sass/**/*', bluebottlePath+"/**/*"],
        tasks: ['render-sass:dev'],
      },
      css: {
        files: ['static/global/css/**/*.css']
      },
    },
    compass: {
      // live
      dist: {
        options: {
          httpPath: '/static/assets/',
          basePath: 'static/global',
          sassDir: 'sass',
          cssDir: 'css',
          imagesDir: 'images',          
          javascriptsDir: 'js',          
          outputStyle: sassOutputStyle,
          relativeAssets: true,
          noLineComments: true,
          environment: 'production',
          raw: 'preferred_syntax = :scss\n', // Use `raw` since it's not directly available
          importPath: bluebottlePath,
          force: true,     
        }
      },
      // development
      dev: {
        options: {
          httpPath: '/static/assets/',
          basePath: 'static/global',
          sassDir: 'sass',
          cssDir: 'css',
          imagesDir: 'images',          
          javascriptsDir: 'js',          
          outputStyle: sassOutputStyle,
          relativeAssets: true,
          noLineComments: false,
          raw: 'preferred_syntax = :scss\n', // Use `raw` since it's not directly available  
          importPath: bluebottlePath,
          force: false,
        }
      }
    }    
  });

  grunt.registerTask('render-sass:dev', 'Alias for "compass:dev" task with relative bluebottle path.', function () {
    bluebottlePath = ["../bluebottle/bluebottle/common/static/sass"];

    grunt.task.run('compass:dev');
  });
  grunt.registerTask('render-sass:test', ['compass:dist']);
  grunt.registerTask('render-sass:live', 'Alias for "compass:dist" task with compressed sass.', function() {
    sassOutputStyle = "compressed";

    grunt.task.run('compass:dist');
  });
  grunt.registerTask('sassRender', ['sass:dist']);
  grunt.registerTask('build:css', ['sass:dist', 'compass:dist']);
}