// *** STUFF YOU DON'T NEED TO TOUCH ***

URL = window.URL || window.webkitURL;
var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext

var supportive_sentences = ['let it all out', 'say how you feel', 'i\'m here for you', 'release it all', 'keep talking about it']

// ** STUFF YOU NEED TO TOUCH **
// CONNECT START, STOP, AND PAUSE FUNCTIONALITY TO ANY BUTTON YOU WANT

// THIS IS TO GET THE BUTTON(S) THAT RECORD / STOP / PAUSE
var recordButton = document.getElementById("recordButton");
// var stopButton = document.getElementById("stopButton");
// var pauseButton = document.getElementById("pauseButton");

// CONNECTS START, STOP, PAUSE FUNCTIONALITY TO THE BUTTONS
recordButton.addEventListener("onclick", recording);
// stopButton.addEventListener("click", stopRecording);
// pauseButton.addEventListener("click", pauseRecording);


function recording() {
	if (document.getElementById("recordButton").value=="OFF")	{
  	document.getElementById("recordButton").value="ON";
		startRecording();
		console.log("ramble clicked");
 	}

  else if(document.getElementById("recordButton").value=="ON"){
   document.getElementById("recordButton").value="OFF";
	 stopRecording();
 }
}
// DONT NEED TO TOUCH THIS

function startRecording() {
	console.log("recordButton clicked");
	recordButton.classList = ['btn btn-danger']
	recordButton.innerHTML = "s t o p"
    var constraints = { audio: true, video:false }

	// recordButton.disabled = true;
	// stopButton.disabled = false;
	// pauseButton.disabled = false

	navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
		console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

		audioContext = new AudioContext();

		document.getElementById("formats").innerHTML = supportive_sentences[Math.floor(Math.random() * 5)]

		gumStream = stream;

		input = audioContext.createMediaStreamSource(stream);

		rec = new Recorder(input,{numChannels:1})

		rec.record()

		console.log("Recording started");

	}).catch(function(err) {
    	// recordButton.disabled = false;
    	// stopButton.disabled = true;
    	// pauseButton.disabled = true
	});
}

// function pauseRecording(){
// 	console.log("pauseButton clicked rec.recording=",rec.recording );
// 	if (rec.recording){
// 		//pause
// 		rec.stop();
// 		pauseButton.innerHTML="Resume";
// 	}else{
// 		//resume
// 		rec.record()
// 		pauseButton.innerHTML="Pause";
//
// 	}
// }

function stopRecording() {
	console.log("stopButton clicked");
	recordButton.classList = ['btn btn-warning']
	recordButton.innerHTML = "l o a d i n g"
	// stopButton.disabled = true;
	// recordButton.disabled = false;
	// pauseButton.disabled = true;

	// pauseButton.innerHTML="Pause";

	rec.stop();

	gumStream.getAudioTracks()[0].stop();

	rec.exportWAV(postToPage);
}

// NEED TO TOUCH THIS

function postToPage(blob) {

    console.log(blob)

    var reader = new FileReader();

    reader.readAsDataURL(blob);
    reader.onloadend = function() {
        var method = "post";
        var form = document.createElement("form");
        form.setAttribute("method", method);
        // NEED TO TOUCH THIS, the '/----' CONTROLS WHAT HANDLER HANDLES THE POST EVENT
	        form.setAttribute("action", '/slider');

        var data = reader.result;
        data = data.substr(data.indexOf(',')+1);

        var hiddenField = document.createElement("input");
        hiddenField.setAttribute("type", "hidden");
        hiddenField.setAttribute("name", "data");
        hiddenField.setAttribute("value", data);
        form.appendChild(hiddenField);
        console.log(form)
        document.body.appendChild(form);
        form.submit();
    }
}
