var express = require("express");
var bodyParser = require('body-parser');
var fs = require('fs');
var app = express();

var viewpath = __dirname + '/views/';

app.get("/",function(req,res){
  res.sendFile(viewpath + "index.html");
});

app.use(bodyParser.urlencoded({extended: true}));

app.post("/confirm", function(req,res){
  var name = req.body.name;
  var studentIDStr = req.body.studentID;
  var email = req.body.email;
  var notifyFrequencyStr = req.body.notifyFrequency;

  var studentIDNum = parseInt(studentIDStr);

  // TODO: Validation
  // Make sure there's no null characters (is that even possible?)
  // 

  if (studentIDNum < 10000000 || studentIDNum >= 100000000) {
    return;
    //res.render('/index', { flash: { type: 'alert-danger', messages: 'ID Number not valid' }});
  } else {
  }

  var notifyFreqDays;
  if (notifyFrequencyStr == 'immediately') notifyFrequencyDays = 0;
  else if (notifyFrequencyStr == 'daily') notifyFrequencyDays = 1;
  else if (notifyFrequencyStr == 'weekly') notifyFrequencyDays = 7;
  else {
    // error
    notifyFrequencyDays = 0;
  }


  // Whether their email is valid (0 or 1), current debt in cents, Email, email
  // frequency in days, their name
  var toWriteToFile = '0\0'+'0\0' + email + '\0' + notifyFrequencyDays + '\0' + name;
  console.log("Writing ``" + toWriteToFile + "'' to file ``" + studentIDStr + "''");
  fs.writeFile(__dirname + "/../data/" + studentIDStr, toWriteToFile, function(err) {
    if(err) {
      return console.log(err);
    }
  });

  // TODO: Send them back to special confirmation page
  res.sendFile(viewpath + "index.html");
});

app.get("*",function(req,res){
  res.sendFile(viewpath + "404.html");
});

app.listen(3000,function(){
  console.log("Live at Port 3000");
});
