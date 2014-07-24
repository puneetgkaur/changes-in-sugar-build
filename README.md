changes-in-sugar-build
======================


1. changes done in apisocket.py
2. added a new folder named cordova in jarabe - which contains native side of various cordova plugins ; so paste the cordova directory in build/out/install/lib/python2.7/site-packages/jarabe/ so that the file inside the cordova folder can be imported in apisocket.py, like : 

  from jarabe.cordova import device as cordova_device

  from jarabe.cordova import accelerometer as cordova_accelerometer

  from jarabe.cordova import camera as cordova_camera
