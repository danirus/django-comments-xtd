const path = require('path');
const webpack = require('webpack');

const STATIC_DIR = path.resolve(__dirname,
                                'django_comments_xtd', 'static',
                                'django_comments_xtd', 'js')
const SOURCE_DIR = path.resolve(STATIC_DIR, 'src');

module.exports = {
  entry: {
    vendor: ['md5', 'react', 'react-dom', 'remarkable'],
    plugin: path.resolve(SOURCE_DIR, 'index.js')
  },
  output: {
    filename: '[name]-2.0.9.js',
    path: STATIC_DIR
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      minChunks: Infinity
    })
  ],
  module: {
    rules: [
      {
        test: /\.jsx?/,
        include: SOURCE_DIR,
        use: [
          { loader: 'babel-loader',
            options: {
              compact: false,
              presets: ["es2015", "react"]
            }
          }
        ]
      }
    ]
  },
  externals: {
    jquery: 'jQuery',
    bootstrap: 'bootstrap',
    django: 'django'
  }
};
