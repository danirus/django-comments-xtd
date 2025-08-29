'use strict';

const path = require('node:path');
const process = require('node:process');
const { babel } = require('@rollup/plugin-babel');
const { nodeResolve } = require('@rollup/plugin-node-resolve');
const replace = require('@rollup/plugin-replace');
const getBanner = require('./banner.js');

const plugins = [
  babel({
    exclude: 'node_modules/**',
    babelHelpers: 'bundled'
  }),
  replace({
    'process.env.NODE_ENV': '"production"',
    preventAssignment: true
  }),
  nodeResolve()
];

const output_file = path.resolve(
  __dirname, '../django_comments_xtd/static/django_comments_xtd/js/djcx.js'
)

module.exports = {
  input: path.resolve(__dirname, 'src/index.js'),
  output: {
    format: 'esm',
    file: output_file,
    banner: getBanner(),
    generatedCode: 'es2015',
  },
  plugins
};
