'use strict';

const path = require('node:path');
const { babel } = require('@rollup/plugin-babel');
const { nodeResolve } = require('@rollup/plugin-node-resolve');

const pkg = require('./package.json');

const STATIC_DIR = path.resolve(
  __dirname, 'django_comments_xtd', 'static', 'django_comments_xtd', 'js'
);
const SOURCE_DIR = path.resolve(STATIC_DIR, 'src');

const plugins = [
  nodeResolve(),
  babel({
    presets: ['@babel/preset-react'],
    exclude: 'node_modules/**',
    babelHelpers: 'bundled',
  }),
];

module.exports = {
  input: path.resolve(SOURCE_DIR, 'index.jsx'),
  output: {
    format: 'iife',
    generatedCode: 'es2015',
    // inlineDynamicImports: true,
    file: path.resolve(STATIC_DIR, `django-comments-xtd-${pkg.version}.js`),
    globals: {
      'django': 'django',
      'react': 'React',
      'react-dom': 'ReactDOM',
      'remarkable': 'remarkable',
    }
  },
  plugins,
  external: ['django', 'react', 'react-dom', 'remarkable'],
};
