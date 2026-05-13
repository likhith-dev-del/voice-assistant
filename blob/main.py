import os
import eel
eel.init('blob')
os.system('start msedge.exe --app="http://localhost:3000/index.html"')
eel.start('index.html', mode=None, host='localhost', block=True)