var path = require('path');
var fs = require('fs');
var http = require('http');
var https = require('https');
var privateKey  = fs.readFileSync(path.join(__dirname + '/ssl/example.com.key'), 'utf8');
var certificate = fs.readFileSync(path.join(__dirname + '/ssl/example.com.crt'), 'utf8');

var credentials = {key: privateKey, cert: certificate};
var express = require('express');
var app = express();

// your express configuration here

var httpsServer = https.createServer(credentials, app);


app.get('/video', (req, res) => {
    console.log("Sending video");
    res.sendFile(path.join(__dirname + '/preview.mp4'));
	console.log("Finished video");
})

app.get('/html', (req, res) => {
    console.log("Sending video");
})



httpsServer.listen(3005);
