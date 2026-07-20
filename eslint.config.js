const eslintConfigPrettier = require('eslint-config-prettier');

module.exports = [
  eslintConfigPrettier,
  {
    ignores: [
      'node_modules/**',
      '.venv/**',
      '.databricks/**',
      '.ruff_cache/**',
      'notebooks/**/*.ipynb',
      'notebooks/outputs/**',
    ],
  },
  {
    files: ['**/*.{js,cjs}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'commonjs',
    },
    rules: {
      curly: 'error',
      eqeqeq: ['error', 'always'],
      'no-console': 'off',
      'no-debugger': 'warn',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-var': 'error',
      'object-shorthand': 'warn',
      'prefer-const': 'warn',
    },
  },
  {
    files: ['**/*.mjs'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
    },
    rules: {
      curly: 'error',
      eqeqeq: ['error', 'always'],
      'no-console': 'off',
      'no-debugger': 'warn',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-var': 'error',
      'object-shorthand': 'warn',
      'prefer-const': 'warn',
    },
  },
];
