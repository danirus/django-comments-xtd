'use strict';

const globalThreshold = 50; // Global code coverage threshold (as a percentage)

module.exports = function configureGrunt(grunt) {
  grunt.initConfig({
    shell: {
      options: {
        stdout: true,
        stderr: true,
        failOnError: true,
      },
      start: {
        command: 'e2e_project/start_server.sh',
      },
      cypress: {
        command: 'npx cypress run',
      },
      stop: {
        command: 'e2e_project/stop_server.sh'
      }
    }
  });

  // grunt.loadNpmTasks('grunt-contrib-qunit');
  grunt.loadNpmTasks('grunt-shell');

  grunt.registerTask('test', ['shell:start', 'shell:cypress', 'shell:stop']);
  grunt.registerTask('default', ['test']);
};
