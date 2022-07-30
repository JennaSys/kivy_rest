# Kivy REST API Demo Application
A [Kivy](https://kivy.org) based CRUD demo application that makes use of a full REST API (via HTTP GET, POST, PUT, and DELETE) 

### Features
- Uses [KivyMD](https://kivymd.readthedocs.io/en/latest/) v1.0.0-dev Material Design inspired widgets
- Connects to a deployed version of the [IEPUG demo REST API](https://github.com/IEPUG/2022_07_REST-API_2) by default
- The REST API endpont can be changed via settings in the app if you want to run the REST server locally
- Data additions/edits/deletions are only allowed with an authenticated session
- Can run as-is on any platform that supports Python
- Android (see below) and iOS (not tested) builds can be compiled with [buildozer](https://buildozer.readthedocs.io/en/latest/index.html)

### Project Organization
- All application code is in the _src/_ folder
- Build files and folders are in the project root
- Each screen consists of a _py_ file and a _kv_ file as a Python package located in the _src/View/_ folder
- The Kivy screens are imported directly from the **View** package in [_mainapp.kv_](src/mainapp.kv) (where the ScreenManager is)
- The [_apputils.py_](src/apputils.py) module has a few convenience functions for making REST API requests, loading kv files, and using the Snackbar (yes, it's a junk drawer, don't @ me)
- The [_version_util.py_](version_util.py) module is just a simple but handy convenience utility for updating the project version on demand

### Screenshots
<img src="images/Kivy_REST_Demo_List.jpg" width="135" alt="App screen - List"/>&nbsp;&nbsp;<img src="images/Kivy_REST_Demo_Login.jpg" width="135" alt="App screen - Login"/>&nbsp;&nbsp;<img src="images/Kivy_REST_Demo_Edit.jpg" width="135" alt="App screen - Edit"/>&nbsp;&nbsp;<img src="images/Kivy_REST_Demo_About.jpg" width="135" alt="App screen - About"/>&nbsp;&nbsp;<img src="images/Kivy_REST_Demo_Settings.jpg" width="135" alt="App screen - Settings"/>
### Android APK
The APK for the most recent debug build can be downloaded from the [GitHub Workflow section](https://github.com/JennaSys/kivy_rest/actions/workflows/main.yml). Look for the artifacts from the most recent build. The APK will be in a file called _package.zip_
