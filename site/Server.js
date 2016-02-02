var express = require("express");
//var Datastore = require('nedb')
var bodyParser = require('body-parser');
var fs = require('fs');

var app = express();
var router = express.Router();
//var db = new Datastore({filename:__dirname + 'IDEmailData.db', autoload:true});

var path = __dirname + '/views/';

router.use(function (req,res,next) {
  console.log("/" + req.method);
  next();
});

router.get("/",function(req,res){
  //console.log(req.query);
  //console.log('notifyFrequency = ' + req.query['notifyFrequency']);
  res.sendFile(path + "index.html");
});

router.use('/confirm', bodyParser());

router.post("/confirm", function(req,res){
  //console.log(req);

  var name = req.body.name;
  var studentIDStr = req.body.studentID;
  var email = req.body.email;
  var notifyFrequencyStr = req.body.notifyFrequency;

  var studentIDNum = parseInt(studentIDStr);

  // TODO: Validation
  // Make sure there's no null characters (is that even possible?)
  // 

  if (studentIDNum < 10000000 || studentIDNum >= 100000000) {
    console.log("ID Not legit");
    //res.render('/index', { flash: { type: 'alert-danger', messages: 'ID Number not valid' }});
  } else {
    console.log("ID LEGIT");
    //res.sendFile(path + "index.html");
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
  
  //db.insert({name:name, studentID:studentIDNum, email:email, notifyFrequency:notifyFrequencyDays});

  // TODO: Send them back to special confirmation page
  res.sendFile(path + "index.html");
});

app.use("/",router);

app.use("*",function(req,res){
  res.sendFile(path + "404.html");
});

app.listen(3000,function(){
  console.log("Live at Port 3000");
});
