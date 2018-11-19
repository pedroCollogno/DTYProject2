var path = require("path");

module.exports = {
  entry: path.resolve(__dirname, "src") + "/index.js",
  output: {
    path: path.resolve(__dirname, "dist") + "/app",
    filename: "bundle.js",
    publicPath: "/app/"
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        include: path.resolve(__dirname, "src"),
        loader: "babel-loader",
        query: {
          presets: ["react", "env"]
        }
      },
      {
        test: /\.css$/,
        loader: "style-loader!css-loader"
      },
      {
        test: /\.(png|jpg)$/,
        loader: 'url-loader'
      },
    ]
  },
  mode: "development",
  node: {
    console: false,
    fs: "empty",
    net: "empty",
    tls: "empty"
  }
};

