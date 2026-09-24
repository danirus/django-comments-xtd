import path from "node:path";
import { fileURLToPath } from "node:url";
import { fixupConfigRules } from "@eslint/compat";
import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import { defineConfig, globalIgnores } from "eslint/config";
import eslintPluginUnicorn from 'eslint-plugin-unicorn';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
});

export default defineConfig([globalIgnores(["build/*", "**/jest.config.js"]), {
  settings: {
    react: {
      "version": "detect",
      "defaultVersion": "18.3.1"
    }
  },
  plugins: {
    unicorn: eslintPluginUnicorn,
  },
  extends: fixupConfigRules(compat.extends(
    "plugin:react/recommended",
    "plugin:import/errors",
    "plugin:import/warnings",
  )),

  rules: {
    indent: ["error", 2, {
      MemberExpression: "off",
      SwitchCase: 1,
    }],

    "max-len": ["error", {
      code: 80,
      comments: 72,
      ignoreUrls: true,
      ignoreRegExpLiterals: true,
      tabWidth: 2,
    }],

    "import/no-unresolved": "off",
    "object-curly-spacing": "off",
    "react/prop-types": "off",
    "unicorn/consistent-destructuring": "off",
    "unicorn/filename-case": "off",
    "unicorn/prefer-module": "off",
    "unicorn/prefer-query-selector": "off",
    "unicorn/prefer-string-replace-all": "off",
    "unicorn/prevent-abbreviations": "off",
  },
}]);
