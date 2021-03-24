const path = require('path');
const webpack = require('webpack');

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');


const devMode = process.env.NODE_ENV !== 'production';
const PRJ_PATH = path.resolve(__dirname, 'django_comments_xtd',
                              'static', 'django_comments_xtd');


const plugins = [
  new webpack.ProgressPlugin(),
  new CleanWebpackPlugin(),
  new MiniCssExtractPlugin({filename: '[name]-[contenthash].css'}),
  new WebpackManifestPlugin()
];

module.exports = {
  mode: devMode ? 'development' : 'production',
  context: __dirname,
  devtool: 'source-map',

  entry: {
    bundle: path.resolve(PRJ_PATH, "js/index.js")
  },

  output: {
    path: path.resolve(PRJ_PATH, "dist"),
    filename: devMode ? '[name]-[contenthash].js' : '[name]-3.0.0.js',
    publicPath: ''
  },

  optimization: {
    splitChunks: {
      cacheGroups: {
        styles: {
          name: 'styles',
          type: 'css/mini-extract',
          chunks: 'all',
          enforce: true
        }
      }
    },
    minimizer: [
      `...`,
      new CssMinimizerPlugin()
    ]
  },

  plugins: plugins,

  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env']
          }
        }
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader'
        ]
      },
      {
        test: /\.(svg|gif|png|eot|woff|ttf)$/,
        use: ['url-loader']
      }
    ]
  }
}