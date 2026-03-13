'use strict';

const globalThreshold = 50; // Global code coverage threshold (as a percentage)

module.exports = function configureGrunt(grunt) {
  grunt.initConfig({
    // qunit: {
    //   options: {
    //     puppeteer: {
    //       disableSetuidSandbox: true,
    //       noSandbox: true,
    //     }
    //   },
    //   all: {
    //     options: {
    //       urls: [
    //         'http://localhost:8333/specs/logged-out/comment-form-spec/'
    //       ]
    //     }
    //   }
    // },
    shell: {
      options: {
        stdout: true,
        stderr: true,
        failOnError: true,
      },
      start: {
        command: 'js/tests/start_server.sh',
      },
      cypress: {
        command: 'npx cypress run',
      },
      stop: {
        command: 'js/tests/stop_server.sh'
      }
    }
  });

  // grunt.loadNpmTasks('grunt-contrib-qunit');
  grunt.loadNpmTasks('grunt-shell');

  grunt.registerTask('test', ['shell:start', 'shell:cypress', 'shell:stop']);
  grunt.registerTask('default', ['test']);
};
