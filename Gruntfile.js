module.exports = function (grunt) {
  var sassOutputStyle = grunt.option('output_style') || 'expanded';
  console.log(sassOutputStyle);
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-ember-template-compiler');
  grunt.loadNpmTasks('grunt-hashres');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-karma');
  grunt.loadNpmTasks('grunt-bower-task'); 
  grunt.loadNpmTasks('grunt-contrib-uglify'); 
  grunt.loadNpmTasks('grunt-microlib');
  grunt.loadNpmTasks('grunt-contrib-compass');
  grunt.loadNpmTasks('grunt-contrib-watch');

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    karma: {
      ci: { configFile: 'test/js/config/karma.conf.js', singleRun: true, browsers: ['PhantomJS'] },
      unit: { configFile: 'test/js/config/karma.conf.js', keepalive: true },
      chrome: { configFile: 'test/js/config/karma.conf.js', keepalive: true, browsers: ['Chrome']  }
      // e2e: { configFile: 'test/js/config/e2e.js', keepalive: true }, // End-to-end / Functional Tests
      // watch: { configFile: 'test/js/config/unit.js', singleRun:false, autoWatch: true, keepalive: true }
    },
    watch: {
      scripts: {
        files: ['apps/static/script/**/*.js', 'ember/static/script/templates/*.handlebars'],
        tasks: ['dev'],
        options: {
          interrupt: true,
          debounceDelay: 250
        }
      },
      scss: {
      	options: {
	      livereload: false,
	    },
        files: ['static/global/sass/**/*',"../bluebottle/bluebottle/common/static/sass/**/*"],
        tasks: ['compass:dev'],
      },
      css: {
        files: ['static/global/css/**/*.css']
      },
    },
    hashres: {
      options: {
        renameFiles: true
      },
      prod: {
        src: ['static/build/js/lib/deps.min.js'],
        dest: 'ember/person/templates/index.html'
      }
    },
    bower: {
      install: {
        options: {
          targetDir: 'static/build/js/components',
          cleanTargetDir: true,
          cleanBowerDir: true,
          install: true,
          copy: true
        }
      },
      cleanup: {
        options: {
          cleanTargetDir: true,
          cleanBowerDir: true,
          install: false,
          copy: false
        }
      }
    },
    concat: {
      dist: {
        src: [
          'static/global/js/vendor/jquery-1.8.3.js',
          'static/build/js/components/jquery-mockjax/jquery.mockjax.js',
          'static/build/js/components/pavlov/pavlov.js',
          'static/global/js/vendor/handlebars-1.0.0.js',
          'static/global/js/vendor/ember-v1.0.0.js',
          'static/global/js/vendor/ember-data-v0.14.js',
          'static/global/js/vendor/ember-data-drf2-adapter.js',
          'static/global/js/plugins/ember.hashbang.js',
          'static/global/js/vendor/globalize.js',
          'static/global/jsi18n/en/*.js',
        ],
        dest: 'static/build/js/lib/deps.js'
      }
    },
    uglify: {
      options: {
        // the banner is inserted at the top of the output
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("dd-mm-yyyy") %> */\n'
      },
      dist: {
        files: {
          '<%= pkg.name %>.min.js': ['<%= concat.dist.dest %>']
        }
      }
    },
    emberhandlebars: {
      compile: {
        options: {
          templateName: function(sourceFile) {
            return sourceFile.match(/\/([0-9|a-z|\.|_]+)\.hbs/i)[1];
          }
        },
        files: ['apps/**/*.hbs'],
        dest: 'static/build/js/lib/tmpl.min.js'
      }
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
          importPath: ["env/src/bluebottle/bluebottle/common/static/sass"]      
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
          importPath: ["../bluebottle/bluebottle/common/static/sass"]      
        }
      }
    }    
  });


  grunt.registerTask('default', ['dev']);
  grunt.registerTask('build', ['bower:install', 'concat:dist']);
  // Add emberhandlebars to dev once it is working
  grunt.registerTask('dev', ['build', 'karma:unit']);
  grunt.registerTask('travis', ['build', 'karma:ci']);
  grunt.registerTask('local', ['dev', 'watch']);
  grunt.registerTask('deploy', ['concat:dist', 'uglify:dist', 'hashres']);
  grunt.registerTask('render-sass:dev', ['compass:dev']);
  grunt.registerTask('render-sass:test', ['compass:dist']);
  grunt.registerTask('render-sass:live', ['compass:dist'], function() {
    sassOutputStyle = "compressed";
  });
}