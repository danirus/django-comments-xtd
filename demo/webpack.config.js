const path = require("path");
const webpack = require("webpack");

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');


const PRJ_PATH = path.resolve(__dirname, 'project');
const devMode = process.env.NODE_ENV !== 'production';


const plugins = [
  new webpack.ProgressPlugin(),
  new CleanWebpackPlugin({ root: PRJ_PATH, verbose: true }),
  new MiniCssExtractPlugin({ filename: '[name]-[contenthash].css' }),
  new WebpackManifestPlugin()
];


module.exports = {
  mode: devMode ? 'development' : 'production',
  context: __dirname,
  devtool: 'source-map',

  entry: {
    global: [
      path.resolve(PRJ_PATH, "frontend/js/base.js"),
      path.resolve(PRJ_PATH, "frontend/js/dropdown.js"),
      path.resolve(PRJ_PATH, "frontend/js/init_language_dropdown.js"),
    ],
    // users: path.resolve(PRJ_PATH, "users/static/js/index.js"),
  },

  output: {
    path: path.resolve(PRJ_PATH, "static/dist"),
    filename: "[name]-[contenthash].js",
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
  },

  devServer: {
    writeToDisk: true,
    contentBase: path.join(PRJ_PATH, "static/dist"),
    port: 3000
  }
}