from PyQt5.QtWidgets import QMessageBox

def requirements():
	messsage_box = QMessageBox()
	messsage_box.setIcon(QMessageBox.Information)
	messsage_box.setText('The Requirements Packages Python will be installed:\n - Numpy\n - Matplotlib\n - Scikit-learn')
	messsage_box.setStandardButtons(QMessageBox.Ok)
	returnValue = messsage_box.exec()
	messsage_box.buttonClicked.connect(installPackage)

def installPackage(returnValue):
	try:
		import sklearn
	except:
		import subprocess
		import sys
		subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'scikit-learn'])

	try:
		import numpy 
	except:
		import subprocess
		import sys
		subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])

	try:
		import matplotlib 
	except:
		import subprocess
		import sys
		subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'matplotlib'])