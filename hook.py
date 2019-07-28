import frida
import sys

session = frida.get_usb_device().attach("com.tencent.mm")
target = sys.argv[1]
script = session.create_script("""


var c = null;
var target = """ + target + """;
var curSteps = 0;


function addSteps(){
	Java.perform(function(){


		var spoofEventConst = Java.use("android.hardware.SensorEvent");
		var spoofEvent = spoofEventConst.$new(1);
		var sys = Java.use("java.lang.System");
		var curtime = sys.nanoTime();
		var values = Java.array("float", [curSteps]);
		spoofEvent.values.value = values;
		var timestamp = Java.use("java.lang.Long");
		timestamp.value = curtime;
		var acc = Java.use("java.lang.Integer");
		acc.value = 3;
		spoofEvent.accuracy = acc;
		spoofEvent.timestamp = timestamp;

		c.onSensorChanged(spoofEvent);
	});

	if (curSteps < target)
	{
		setTimeout(function(){
			addSteps(50);
			curSteps += 50;
		}, 1000);
	}else{
		console.log("Finished adding steps.");
	}

};


Java.perform(function (){
	Java.choose("com.tencent.mm.plugin.sport.model.c", {
		onMatch: function (inst){
			c = inst;
		},
		onComplete: function(){
			addSteps();
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