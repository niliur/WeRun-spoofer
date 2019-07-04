import frida
import sys

session = frida.get_usb_device().attach("com.tencent.mm")
script = session.create_script("""


var c = null;
var target = 60000;

function shadyHooks(){
	Java.perform(function(){

		addSteps(0);



		c.onSensorChanged.implementation = function(event){
			console.log(event.values.value[0]);
			//spoofEvent.timestamp.value = event.timestamp.value;
			//event.values.value[0] = 1066;
			//console.log("sensor event");
			//console.log(this.rjr.value + "rjr?");
			//console.log(this.rjs.value + "rjs?");
			this.onSensorChanged(event);
			//console.log("worked?");
			//console.log("sensor event after");
			//console.log(this.rjr.value + "rjr?");
			//console.log(this.rjs.value + "rjs?");
		};
	});
		
};

function addSteps(curIter){
	Java.perform(function(){

		curIter = curIter !== undefined ? curIter : 0;




		console.log("hooked");
		var spoofEventConst = Java.use("android.hardware.SensorEvent");
		var spoofEvent = spoofEventConst.$new(1);
		var sys = Java.use("java.lang.System");
		var curtime = sys.nanoTime();
		var values = Java.array("float", [curIter]);
		spoofEvent.values.value = values;
		var timestamp = Java.use("java.lang.Long");
		timestamp.value = curtime;
		var acc = Java.use("java.lang.Integer");
		acc.value = 3;
		spoofEvent.accuracy = acc;
		spoofEvent.timestamp = timestamp;

		c.onSensorChanged(spoofEvent);
	});

	if (curIter < target)
	{
		setTimeout(function(){
			addSteps(curIter + 50);
		}, 1000);
	}

};


Java.perform(function (){
	Java.choose("com.tencent.mm.plugin.sport.model.c", {
		onMatch: function (inst){
			console.log("Found instance: " + inst);
			c = inst;
			// should only be one of these
		},
		onComplete: function(){
			console.log("Found all");
			shadyHooks();

		}
	});
});

""")

# Here's some message handling..
# [ It's a little bit more meaningful to read as output :-D
#   Errors get [!] and messages get [i] prefixes. ]
def on_message(message, data):
    if message['type'] == 'error':
        print("[!] " + message['stack'])
    elif message['type'] == 'send':
        print("[i] " + message['payload'])
    else:
        print(message)
script.on('message', on_message)
script.load()
sys.stdin.read()