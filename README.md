# WeRun-spoofer
An application which uses Frida to spoof the WeChat WeRun app and increase step count for android.

Steps to use: 
1. Install [Frida](https://www.frida.re/) on your Android device.
2. Install Frida on your computer with  `pip install frida-tools` or follow the installation guide [here](https://www.frida.re/docs/installation/)
3. Open the WeChat app on the android device and login to the account you wish to add steps to. 
4. Call the script with `python hook.py [stepcount]` where [stepcount] is the desired number of steps. 

Working on version weixin704android1420