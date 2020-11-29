// npm install
// node server.js

const express = require('express')
var path = require('path');
const app = express()
const port = process.env.PORT || 3000 // for heroku
const { execFile } = require('child_process');

app.get('/HTML', (req, res) => {
    console.log("Sending HTML");
    //var ip = req.connection.remoteAddress;

    //const python = execFile('python', ['serverSniffer.py', ip.toString()]);
    //python.stdout.on('data', function(data) {
    //    console.log('Server Sniffer says:\n' + data.toString());
    //});
    res.sendFile(path.join(__dirname + '/index.html'));
})

app.get('/video', (req, res) => {
    console.log("Sending video");
    res.sendFile(path.join(__dirname + '/preview.mp4'));
})

app.get('/packets', (req, res) => {
    console.log("Sending Python Sniff");
    var formattedIP = (req.connection.remoteAddress).replaceAll("::ffff:", "").replaceAll(".", "_").replaceAll(":", "-");
    console.log("Formatted IP: " + formattedIP);
    res.sendFile(path.join(__dirname + "/sniff" + formattedIP));
})

app.get('/startsniff', (req, res) => {
    console.log("Starting Sniff");
    var ip = req.connection.remoteAddress;

    const python = execFile('python', ['serverSniffer.py', ip.toString()]);
    python.stdout.on('data', function (data) {
        console.log('Server Sniffer says:\n' + data.toString());
    });
    res.sendStatus(200);
})

app.listen(port, () => {
    console.log(`UZH-MAP listening at http://localhost:${port}`)
})


//for javascript's stupid string replacement
String.prototype.replaceAll = function (str1, str2, ignore) {
    return this.replace(new RegExp(str1.replace(/([\/\,\!\\\^\$\{\}\[\]\(\)\.\*\+\?\|\<\>\-\&])/g, "\\$&"), (ignore ? "gi" : "g")), (typeof (str2) == "string") ? str2.replace(/\$/g, "$$$$") : str2);
}
