// npm install
// node server.js

const express = require('express')
var path = require('path');
const app = express()
const port = process.env.PORT || 3000 // for heroku

app.get('/HTML', (req, res) => {
  console.log("Sending HTML");
  res.sendFile(path.join(__dirname + '/index.html'));
})
app.get('/video', (req, res) => {
    console.log("Sending video");
  res.sendFile(path.join(__dirname + '/preview.mp4'));
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})
