// const fs = require('node:fs/promises');
// const path = require('node:path');
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default async function getBanner() {
  const pkgJson = path.join(__dirname, '../package.json');
  const pkg = JSON.parse(await fs.readFile(pkgJson, 'utf8'));
  const year = new Date().getFullYear();

  return `/*!
  * django-comments-xtd v${pkg.version} (${pkg.homepage}).
  * Copyright ${year} ${pkg.author}.
  * Licensed under MIT (https://github.com/danirus/django-comments-xtd/blob/main/LICENSE).
  */`;
}
