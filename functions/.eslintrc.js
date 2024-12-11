module.exports = {
  root: true,
  env: {
    es6: true,
    node: true,
  },
  extends: [
    "eslint:recommended"
  ],
  rules: {
    "quotes": "off",
    "indent": "off",
    "max-len": "off",
    "object-curly-spacing": "off",
    "no-trailing-spaces": "off",
    "eol-last": "off",
    "no-unused-vars": ["error", { "argsIgnorePattern": "^_" }]  // This line is new
  },
  parserOptions: {
    ecmaVersion: 2018,
  },
};