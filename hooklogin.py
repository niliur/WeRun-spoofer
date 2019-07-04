import frida
import sys
import subprocess
import re
import threading
import time
username = sys.argv[1]
password = sys.argv[2]
steps = sys.argv[3]

# Here's some message handling..
# [ It's a little bit more meaningful to read as output :-D
#   Errors get [!] and messages get [i] prefixes. ]

found_plugin = False

def get_k_interrupt(e):
    try:
        print("helloo?")
        sys.stdin.read()
    except KeyboardInterrupt:
        print("did this shit work")
        e.set()



def on_message(message, data):
    if message['type'] == 'error':
        print("[!] " + message['stack'])
    elif message['type'] == 'send':
        data = message['payload'];
        if data == "login failed":
            print("[f] login failed, finishing...")
            reset()
            print("[f] ending script")
            exit_flag.set()
        elif data == "login success":
            print("[f] login success, continuing")

        elif data == "found plugin":
            print("[f] adding steps...")
            script.post({"steps": steps})
            found_plugin = True

        elif data == "plugin failed":
            print("[f] sports plugin failed... contact niliur@outlook.com if this persists")
            reset()
            print("[f] ending script")
            exit_flag.set()
        elif data.startswith("curstep"):
            curstep = data.split(":")[1]
            print("[f] currently at: " + curstep)

        elif data == "logging out":
            print("[f] logging out wechat")
            time.sleep(10)
            print("[f] application finished")
            exit_flag.set()
        else:
            print("[f] wtf is this? " + data)

    else:
        print(message)

def reset():
    print("attempting to kill wechat")
    runningApps = subprocess.run(["frida-ps", "-Ua"], stdout=subprocess.PIPE)
    runningApps = runningApps.stdout.decode('utf-8')
    #print(runningApps)
    pid = re.search('(\d+)(?=\s+WeChat)', runningApps)
    if pid is not None:
        #print(pid)
        subprocess.run(["frida-kill", "-D", "9888d3454151523837", pid.group(0)], stdout=subprocess.PIPE)



try:
    # just call abort incase shit is going down
    reset()

    device  = frida.get_usb_device()
    pid     = device.spawn(['com.tencent.mm'])
    session = device.attach(pid)
    engaged = True
    #session = frida.get_usb_device().attach("com.tencent.mm")
    script = session.create_script("""

    var username = \"""" + username + """\"
    var password = \"""" + password + """\"

    var mainFrag = null;
    var sportsPlugin = null;


    function logoutWechat()
    {
        Java.perform(function()
        {
            var logout = Java.use("com/tencent/mm/plugin/setting/ui/setting/SettingsUI");

            logout.onResume.implementation = function()
            {
                this.onResume();
                logout.g(this);
            }

            var intent = Java.use('android.content.Intent');

            send("logging out");
            var res = intent.$new(mainFrag.getContext(), logout.class);
            mainFrag.startActivity(res);




        });





    }

    function addSteps(curIter, tarIter)
    {
        Java.perform(function(){

            curIter = curIter !== undefined ? curIter : 0;


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

            sportsPlugin.onSensorChanged(spoofEvent);
        });

        if (curIter < tarIter)
        {
            var variable = Math.floor(Math.random() * 15) - 7;
            var tvariable = Math.floor(Math.random()*700);
            var curstep = Math.min(tarIter, curIter + 50 + variable);
            send("curstep:" + curstep);

            setTimeout(function(){
                addSteps(curstep, tarIter);
            }, 600 + tvariable);
        }
        else
        {
            logoutWechat();
        }
    }



    function checkSportPlugin()
    {
        Java.perform(function (){
            var found = false;
            Java.choose("com.tencent.mm.plugin.sport.model.c", {
                onMatch: function (inst){
                    if (!found)
                    {
                        sportsPlugin = inst;
                    }
                    else
                    {
                        console.log("found sports plugin twice?");
                    }
                    found = true;
                    // should only be one of these
                },
                onComplete: function(){
                    if (found)
                    {
                        send("found plugin");
                        var steps;
                        recv(function(ob){
                            steps = ob.steps;
                        }).wait();
                        addSteps(0,steps);
                    }
                    else
                    {
                        send("plugin failed");
                    }
                    //shadyHooks();

                }
            });
        });
    }


    function checkWechatLogin()
    {

        Java.perform(function()
        {
            var found = false;

            Java.choose('com/tencent/mm/ui/conversation/MainUI', {
                onMatch: function (inst)
                {
                    found = true;
                    mainFrag = inst;
                    if (found)
                    {
                        console.log("found this more than once??");
                    }
                },
                onComplete: function()
                {
                    if (found)
                    {
                        var steps;
                        send("login success");
                        checkSportPlugin();

                    }
                    else
                    {
                        send("login failed");

                    }

                }
            });


        });
    }


    Java.perform(function (){

        // This is the login screen for the account memorized
        var activity = Java.use("com.tencent.mm.plugin.account.ui.LoginPasswordUI");

        //This is the mobile login using sms
        var activity2 = Java.use("com.tencent.mm.plugin.account.ui.MobileInputUI");

        // This is login with password / username
        var activity3 = Java.use("com.tencent.mm.plugin.account.ui.LoginUI");

        var intent = Java.use('android.content.Intent');

        // jump start to user/password login
        activity.onCreate.implementation = function(a)
        {
            this.onCreate(a);

            var res = intent.$new(this, activity3.class);
            this.startActivity(res);
        }
        activity3.onResume.implementation = function()
        {
            console.log("login activity started");
            this.onResume();

            //activity3.e(this);
            var aqu = activity3.class.getDeclaredMethod("aqU", null);

            var editTextUsername = this.gCS.value;
            var editTextPassword = this.gCT.value;
            console.log("login action 2");

            editTextUsername.ajp(username);
            editTextPassword.ajp(password);
            aqu.setAccessible(true);
            aqu.invoke(this, null);

            // check login success after 10 seconds
            setTimeout(function(){
                checkWechatLogin();
            }, 10000);
        }
    });

    """)
    
    script.on('message', on_message)
    script.load()
    #sys.stdin.read()
    
    #Call resume *after* script.load(), otherwise onCreate won't get hooked.
    #device.resume(pid)
    exit_flag = threading.Event()



    # not using wait here because for some reason wait is blocking keyboard interrupts on windows
    max_iteration = 130 
    cur_iteration = 0
    while not exit_flag.is_set():
        maxi = (int(steps)/50 + max_iteration) if found_plugin else max_iteration
        if cur_iteration > maxi:
            print("[f] application reached timeout period, exiting")
            reset()
            sys.exit()
        else:
            cur_iteration = cur_iteration + 1
            time.sleep(1)


    print("[f] application finished, exiting")
    reset()

except KeyboardInterrupt:
    print("[f] recieved KeyboardInterrupt")
    reset()
    sys.exit()




            # var methods = activity3.class.getDeclaredMethods();
            # for (i = 0; i < methods.length; i++)
            # {
            #     console.log(methods[i].toString());
            # }


        #some logout detection stuff

        #             logout.a.overload('com.tencent.mm.ui.base.preference.f', 'com.tencent.mm.ui.base.preference.Preference').implementation = function(a,b)
        # {
        #     console.log("logout 2?");
        #     //console.log(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));
        #     return this.a(a,b);
        # }

        # var fb = Java.use("com/tencent/mm/ui/base/h");
        # fb.a.overload('android.content.Context', 'boolean', 'java.lang.String', 'java.lang.String', 'java.lang.String', 'java.lang.String', 'android.content.DialogInterface$OnClickListener', 'android.content.DialogInterface$OnClickListener').implementation = 
        # function(a,b,c,d,e,f,g,h)
        # {
        #     console.log("logout 28?");
        #     return this.a(a,b,c,d,e,f,g,h);
        # }

        # var dialog = Java.use("com/tencent/mm/ui/widget/a/c");
        # dialog.a.overload('com.tencent.mm.ui.widget.a.a').implementation = function(a)
        # {
        #     console.log("logout dialog?");
        #     var ret = this.a(a);
        #     return ret;
        # }
        # dialog.a.overload('java.lang.CharSequence', 'boolean', 'android.content.DialogInterface$OnClickListener').implementation = function(a, b, c)
        # {
        #     console.log("logout dialog a overload");
        #     console.log(a);
        #     console.log(b);
        #     console.log(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));

        #     console.log('did it work?');
            

        #     //this.a(a, b, c);
        # }

        # var dialog2 = Java.use("com/tencent/mm/ui/widget/a/c$a");
        # dialog2.a.overload('boolean', 'android.content.DialogInterface$OnClickListener').implementation = function(a,b)
        # {
        #     console.log("c2a a");
        #     console.log(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));
        #     return dialog2.a(a,b);
        # }

        # var dialog3 = Java.use("com/tencent/mm/ui/widget/a/c$a");
        # dialog3.a.overload('android.content.DialogInterface$OnClickListener').implementation = function(a)
        # {
        #     console.log("c3a a");
        #     console.log(Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new()));
        #     return dialog3.a(a);
        # }





        # var mainUI = Java.use("com/tencent/mm/ui/conversation/MainUI");
        # var logout = Java.use("com/tencent/mm/plugin/setting/ui/setting/SettingsUI");


        # mainUI.onCreate.implementation = function(a)
        # {
        #     console.log("login success");
        #     this.onCreate(a);
        #     var res = intent.$new(this.getContext(), logout.class);

        #     this.startActivity(res);


        # }

