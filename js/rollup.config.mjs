'use strict';

import path from 'node:path';
import process from 'node:process';
import getBanner from './banner.js';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const output_file = path.resolve(
  __dirname, '../django_comments_xtd/static/django_comments_xtd/js/djcx.js'
)

export default {
  input: path.resolve(__dirname, 'src/index.js'),
  output: {
    format: 'es',
    file: output_file,
    banner: getBanner(),
    generatedCode: 'es2015',
  },
  plugins: []
};
