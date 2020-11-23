// npm install
// node server.js

const express = require('express')
var path = require('path');
const app = express()
const port = process.env.PORT || 3000 // for heroku
const axios = require('axios');



app.get('/HTML', (req, res) => {
  console.log("Sending HTML");
  var ip = req.connection.remoteAddress
  var str1 = "http://127.0.0.1:3005/"; //executes the python script
  var str2 = ip;
  var micros = str1.concat(str2);
  axios.get(micros)
  .then(response => {
    console.log(response);
    console.log(response.data.explanation);
  })
  .catch(error => {
    console.log(error);
  });
  res.sendFile(path.join(__dirname + '/index.html'));
  //send scapy file res.sendFile(path.join(__dirname + '/index.html'));
})
app.get('/video', (req, res) => {
    console.log("Sending video");
  res.sendFile(path.join(__dirname + '/preview.mp4'));
})

app.get('/HTMLsniff', (req, res) => {
    console.log("Sending Python Sniff");
	var ip = req.connection.remoteAddress
  res.sendFile(path.join(__dirname + "/sniff" + ip));
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})
