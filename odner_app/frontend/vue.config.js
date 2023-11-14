const path = require('path');
const fs = require('fs')
module.exports = {
  publicPath: process.env.NODE_ENV === 'production' ? '/llm/' : '/',
  outputDir: 'dist',
  indexPath: 'index.html',
  devServer: {
allowedHosts: 'all', 
host: 'ondemandner.isti.cnr.it',
open: true, hot: true,    
//https: {
//          key: fs.readFileSync('/etc/letsencrypt/live/ondemandner.isti.cnr.it/privkey.pem'),
//          cert: fs.readFileSync('/etc/letsencrypt/live/ondemandner.isti.cnr.it/cert.pem'),
//          ca: fs.readFileSync('/etc/letsencrypt/live/ondemandner.isti.cnr.it/fullchain.pem'),
//        },
server: {
      type: 'https',
      options: {
//        ca: '/etc/letsencrypt/live/ondemandner.isti.cnr.it/fullchain.pem',
//        key: '/etc/letsencrypt/live/ondemandner.isti.cnr.it/privkey.pem',
//        cert: '/etc/letsencrypt/live/ondemandner.isti.cnr.it/cert.pem',
//          passphrase: 'webpack-dev-server',
          key: fs.readFileSync('/etc/letsencrypt/live/ondemandner.isti.cnr.it/privkey.pem'),
          cert: fs.readFileSync('/etc/letsencrypt/live/ondemandner.isti.cnr.it/cert.pem'),
          ca: fs.readFileSync('/etc/letsencrypt/live/ondemandner.isti.cnr.it/fullchain.pem'),

//        requestCert: true,
      },
},
port: 8080,
    proxy: {
      '/api': {
        target: 'https://ondemandner.isti.cnr.it/llm/', // Replace with your Django server URL
        changeOrigin: true,
        pathRewrite: {
          '^/api': '',
        },
      },
    },
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
  },
};

