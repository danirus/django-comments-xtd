const fs = require('node:fs/promises');
const path = require('node:path');

async function getBanner() {
  const pkgJson = path.join(__dirname, '../package.json');
  const pkg = JSON.parse(await fs.readFile(pkgJson, 'utf8'));
  const year = new Date().getFullYear();

  return `/*!
  * sphinx-colorschemed-images v${pkg.version} (${pkg.homepage}).
  * Copyright ${year} ${pkg.author}.
  * Licensed under MIT (https://github.com/danirus/sphinx-colorschemed-images/blob/main/LICENSE).
  */`;
}

module.exports = getBanner;
