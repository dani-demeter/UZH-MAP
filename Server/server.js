// npm install
// node server.js

const express = require('express')
var path = require('path');
const app = express()
const port = 3000

app.get('/', (req, res) => {
  // res.send('Hello World!')
  res.sendFile(path.join(__dirname + '/preview.mp4'));
  // res.sendFile(path.join(__dirname + '/index.html'));
})

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`)
})
