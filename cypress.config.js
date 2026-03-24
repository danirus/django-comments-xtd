const { defineConfig } = require("cypress");

module.exports = defineConfig({
  allowCypressEnv: false,
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: 'http://localhost:8333',
    supportFile: 'e2e_project/cypress/support/index.js',
    specPattern: 'e2e_project/cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    // fileServerFolder: 'js/tests',
  },
});
