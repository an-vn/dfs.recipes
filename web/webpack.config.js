const CopyPlugin = require('copy-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');

module.exports = {
    entry: './index.js',
    output: {
        clean: true,
        // path: path.resolve(__dirname, 'dist'),
        path: path.join(__dirname, '..', 'src', 'dfs_recipes', 'static'),
        // filename: 'index.js',
        filename: '[name].bundle.js',
        // filename: '[name].[contenthash].bundle.js',
        // asyncChunks: true,
        // chunkFilename: '[id].js',
    },
    module: {
        rules: [
            {
                test: /\.(js|mjs|cjs)$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        targets: 'defaults',
                        presets: [
                            ['@babel/preset-env']
                        ]
                    }
                }
            },
            {
                test: /\.css$/i,
                use: ['style-loader', 'css-loader'],
            },
            {
                test: /\.(png|svg|jpe?g|gif)$/i,
                type: 'asset/resource',
            },
            {
                test: /\.(woff|woff2|eot|ttf|otf)$/i,
                type: 'asset/resource',
            },
            {
                test: /\.json$/i,
                type: 'json',
            },
        ]
    },
    mode: 'development',
    experiments: {
        asyncWebAssembly: true,
        topLevelAwait: true,
    },
    plugins: [
        new HtmlWebpackPlugin({
            title: 'DFS Recipes',
            template: path.resolve(__dirname, 'index.html'),
            inject: true,
        }),
        new CopyPlugin({
            patterns: [
                { from: path.resolve(__dirname, 'assets'), to: 'assets' },
                { from: path.resolve(__dirname, 'data'), to: 'data' },
            ],
        }),
    ],
    devtool: 'eval-source-map',
    resolve: {
        extensions: ['.js', '.json'],
    },
    devServer: {
        compress: true,
        port: 3000,
        proxy: [
            {
                context: ['/api'],
                target: 'https://localhost:8000/',
                secure: false,
            },
        ],
    },
    optimization: {
        runtimeChunk: 'single',
    },
    cache: false,
};
