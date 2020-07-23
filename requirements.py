from PyQt5.QtWidgets import QMessageBox
import subprocess
import sys

def requirements():
	messsage_box = QMessageBox()
	messsage_box.setIcon(QMessageBox.Information)
	messsage_box.setText('The Requirements Packages Python will be installed:\n - Numpy\n - Matplotlib\n - Scikit-learn')
	messsage_box.setStandardButtons(QMessageBox.Ok)
	returnValue = messsage_box.exec()
	messsage_box.buttonClicked.connect(packageInstaller)

def packageInstaller():
	# install package
	subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])