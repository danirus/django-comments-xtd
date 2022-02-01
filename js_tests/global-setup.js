const path = require('path');

const { setup: setupDevServer } = require('jest-dev-server');

const server_path = path.resolve(__dirname, "serve_static.js");

module.exports = async function globalSetup() {
    await setupDevServer({
        command: `node ${server_path}`,
        launchTimeout: 50000,
        port: 3000,
        debug: true
    });
};
