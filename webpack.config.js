const path = require('path');
const webpack = require('webpack');

const STATIC_DIR = path.resolve(__dirname,
                                'django_comments_xtd', 'static',
                                'django_comments_xtd', 'js');
const SOURCE_DIR = path.resolve(STATIC_DIR, 'src');

module.exports = {
  mode: "production",
  devtool: 'source-map',
  entry: {
    plugin: path.resolve(SOURCE_DIR, 'index.js')
  },
  output: {
    filename: '[name]-2.8.2.js',
    path: STATIC_DIR
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        default: false,
        vendors: false,
        vendor: {
          chunks: 'all',
          test: /node_modules/
        }
      }
    },
    minimize: true
  },
  module: {
    rules: [
      {
        test: /\.jsx?/,
        include: SOURCE_DIR,
        use: {
          loader: 'babel-loader'
        }
      }
    ]
  },
  externals: {
    bootstrap: 'bootstrap',
    django: 'django',
    jquery: 'jQuery',
    react: 'React',
    'react-dom': 'ReactDOM'
  }
};
