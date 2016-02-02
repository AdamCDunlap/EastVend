var express = require('express');
var fs = require('fs');
var bootstrap = require('bootstrap');
var app = express();

app.use(express.static('public'));

app.get('/', function (req, res) {
  res.send('Hello World!');
});

app.get('/example', function (req, res) {
  res.sendFile(__dirname + '/example.html');
});

app.get('/form', function (req, res) {
  res.sendFile(__dirname + '/myform.html')
  // fs.readFile('gform.html', 'utf8', function (err, data) {
  //   if (err) {
  //     console.log("Error reading the gform.html");
  //   } else {
  //     res.set('Content-Type', 'text/html');

  //     res.send(data);
  //   }
  // });
});

app.get('/submit_form', function (req, res) {

   // Prepare output in JSON format
   response = {
       id : req.query.id_num,
       email : req.query.email
   };
   console.log(response);
   res.end(JSON.stringify(response));
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});

