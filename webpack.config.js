const path = require('path');
const webpack = require('webpack');

const STATIC_DIR = path.resolve(__dirname,
                                'django_comments_xtd', 'static',
                                'django_comments_xtd', 'js')
const SOURCE_DIR = path.resolve(STATIC_DIR, 'src');

module.exports = {
  entry: {
    vendor: ['react', 'react-dom', 'jquery', 'bootstrap'],
    plugin: path.resolve(SOURCE_DIR, 'index.js')
      // path.resolve(SOURCE_DIR, 'react.plugin.jsx'),
    //   path.resolve(SOURCE_DIR, 'index.js'),
    //   path.resolve(SOURCE_DIR, 'comment.jsx'),
    //   path.resolve(SOURCE_DIR, 'commentform.jsx'),
    //   path.resolve(SOURCE_DIR, 'commenttree.jsx')
    // ]
  },
  output: {
    // filename: '[name].[chunkhash].js',
    filename: '[name]-1.7.1.js',
    path: STATIC_DIR
  },
  plugins: [
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',  // Specify the common bundle's name.
      minChunks: Infinity
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      "window.jQuery": 'jquery'
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
  }
};
