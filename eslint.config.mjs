import { fixupConfigRules } from "@eslint/compat";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all
});

export default [{
  ignores: [
    ".eggs/*",
    ".tox/*",
    "build/*",
    "dist/*",
    "django_comments_xtd/*",
    "docs/*",
    "example/*",
    "scss/*",
    "venv/*",
  ],
}, ...fixupConfigRules(compat.extends(
  "plugin:import/errors",
  "plugin:import/warnings",
  "plugin:unicorn/recommended",
)), {
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

    "unicorn/filename-case": [
      "error",
      {
        "case": "snakeCase"
      }
    ],

    "object-curly-spacing": "off",
    "unicorn/expiring-todo-comments": "off",
    "unicorn/prefer-module": "off",
    "unicorn/prefer-query-selector": "off",
    "unicorn/prevent-abbreviations": "off",
  },
}];
