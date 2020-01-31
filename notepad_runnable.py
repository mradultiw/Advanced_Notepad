from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget,QFileDialog, QTextEdit, QMessageBox, QFontDialog, QColorDialog
from PyQt5 import QtGui,QtWidgets, QtCore, QtPrintSupport
from PyQt5.QtGui import QTextCursor
import sys
from os import getcwd,chdir
from main import *

'''change TabMovable to Flase else code will break'''

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tabWidget.tabCloseRequested['int'].connect(self.removeTab)
        self.tabCounter=0
        
        self.destroyed.connect(self.closeEvent)
        
        self.TabDictionary={}
        
        self.createNewFile()#Default Tab        
        ### open
        self.ui.actionNew_Tab.triggered.connect(self.openInNewTab)
        self.ui.actionCurrent_Tab.triggered.connect(self.openInCurrentTab)   
        ### New        
        self.ui.actionNew.triggered.connect(self.createNewFile)
        ### Save        
        self.ui.actionSave.triggered.connect(self.saveCurrentFile)
        ### SaveAs        
        self.ui.actionSaveAs.triggered.connect(self.saveAsCurrentFile)
        ### Time_Date
        self.ui.actionTime_Date.triggered.connect(self.insertTime_Date)
        ### print
        self.ui.actionPrint.triggered.connect(self.printFile)
        ###Font
        self.ui.actionFont.triggered.connect(self.fontDialogBox)
        ###Color
        self.ui.actionColor.triggered.connect(self.colorDialogBox)

        
        timer=QtCore.QTimer(self)
        timer.start(1500)
        timer.timeout.connect(self.CurrentTabNameUpdate)
        self.show()
    
    def fontDialogBox(self):
        dialog=QFontDialog()
        dialog.setModal(True)
        font,ok=dialog.getFont()
        CurrentTab=self.ui.tabWidget.currentWidget()
        if ok and font:
            CurrentTab.findChild(QTextEdit).setFont(font)
            
    def colorDialogBox(self):
        dialog=QColorDialog()
        dialog.setModal(True)
        col=dialog.getColor()
        CurrentTab=self.ui.tabWidget.currentWidget()
        if col.isValid():
            CurrentTab.findChild(QTextEdit).setTextColor(col)
    
    def closeEvent(self,event=None):
        initials=[self.TabDictionary[tab][0][0] for tab in self.TabDictionary]
        if '*' in initials:
                msg=QMessageBox()
                msg.setModal(True)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Message")
                msg.setText("<b>Some files have been changed but not saved!<b>")
                msg.setInformativeText("Do you want to save changes?")
                msg.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint |
                              QtCore.Qt.WindowTitleHint)
                msg.setStandardButtons(QMessageBox.Yes|QMessageBox.Discard)
                msg.setDefaultButton(QMessageBox.Yes)
                msg.button(QMessageBox.Discard).clicked.connect(event.accept)
                msg.button(QMessageBox.Yes).clicked.connect(event.ignore)
                msg.exec_()
            
    def printFile(self,textBody):
        textBody=self.ui.tabWidget.currentWidget().findChild(QTextEdit)
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dialog = QtPrintSupport.QPrintPreviewDialog(printer,self)
        dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint |
                              QtCore.Qt.WindowTitleHint |QtCore.Qt.WindowCloseButtonHint)
        dialog.paintRequested.connect(textBody.print_)
        dialog.exec_()        
    
    def insertTime_Date(self):
        CurrentTab=self.ui.tabWidget.currentWidget()
        time=QtCore.QTime.currentTime().toString("hh : mm : ss")
        date=QtCore.QDate.currentDate().toString("dddd, MMM yyyy")
        cursor = QTextCursor(CurrentTab.findChild(QTextEdit).textCursor())
        cursor.insertText(date+", "+time)
    
    def createNewFile(self):
        self.InsertNewTab()
    
    def openInNewTab(self):
        self.InsertNewTab()
        if not self.fileDialogBoxOpenFile():
            self.tabCounter-=1
            del self.TabDictionary[self.ui.tabWidget.currentIndex()]
            self.ui.tabWidget.removeTab(self.ui.tabWidget.currentIndex())
        
    def openInCurrentTab(self):
        ###check previous(if any) is saved or not
        if self.TabDictionary[self.ui.tabWidget.currentIndex()][0][0]=='*':
            msg=QMessageBox()
            msg.setModal(True)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Message")
            msg.setText("<b>Current file Changed!<b>")
            msg.setInformativeText("Do you want to save changes?")
            msg.setDetailedText("On successful opening of new file in current tab,\
                                any unsaved changes will be lost")
            msg.setStandardButtons(QMessageBox.Save|QMessageBox.Discard)
            msg.setDefaultButton(QMessageBox.Save)
            msg.button(QMessageBox.Save).clicked.connect(self.saveCurrentFile)
            msg.exec_()
        self.fileDialogBoxOpenFile()

    def saveCurrentFile(self):
        return self.fileDialogBoxSaveFile()
    
    def saveAsCurrentFile(self):
        previousFileInfo=self.TabDictionary[self.ui.tabWidget.currentIndex()]
        self.TabDictionary[self.ui.tabWidget.currentIndex()]=None
        if not self.fileDialogBoxSaveFile("SaveAs..."):
            self.TabDictionary[self.ui.tabWidget.currentIndex()]=previousFileInfo

    def fileDialogBoxOpenFile(self):
        dialog=QFileDialog()
        dialog.setModal(True)
        filePath,*_=dialog.getOpenFileName(self,"Open File",getcwd(),\
                                           "All Files (*);;Text Files (*.txt)")
        cwd="./"
        if not filePath:
            return False
        
        fileName=""
        for i in range(len(filePath)-1,-1,-1):
            if filePath[i]=='/':
                cwd=filePath[:i]
                fileName=filePath[i+1:]
                break
        chdir(cwd)
        if filePath:
            try:
                with open(filePath,'r') as f:
                    data=f.read()
                    #self.ui.textEditContent.clear()
                    #self.ui.textEditContent.append(data)
                    CurrentTab=self.ui.tabWidget.currentWidget()
                    CurrentTab.findChild(QTextEdit).setText(data)
                self.updateTabOnFileOperation(filePath,fileName)
                self.saveCurrentFile()
            except:
                self.showWarningDialog(f"Format of '{fileName}' is not supported")
                return False
        return True
    
    def fileDialogBoxSaveFile(self, windowTitle="Save..."):
        fileInfo=self.TabDictionary[self.ui.tabWidget.currentIndex()]
        
        if fileInfo and fileInfo[1] and fileInfo[0][0]!='*':
            return True
        # fileInfo inside 'if' to make sure it is not None to avoid indexing error
        if fileInfo and fileInfo[1]:
            self.updateTabOnFileOperation(fileInfo[1],fileInfo[0].strip('*'))
            filePath=fileInfo[1]
        else:
            dialog=QFileDialog()
            dialog.setModal(True)
            options=dialog.Options()
            options|=QFileDialog.DontUseNativeDialog
            filePath,*_=QFileDialog.getSaveFileName(self, windowTitle ,getcwd(),\
                                                 "All Files (*);;Text Files (*.txt)",\
                                                     options=options)
            cwd="./"
            for i in range(len(filePath)-1,-1,-1):
                if filePath[i]=='/':
                    cwd=filePath[:i]
                    self.updateTabOnFileOperation(filePath,filePath[i+1:])
                    break
            chdir(cwd)
            
        CurrentTab=self.ui.tabWidget.currentWidget()
        textEditContent=CurrentTab.findChild(QTextEdit)
        if filePath:
            with open(filePath,'w') as f:
                f.write(textEditContent.toPlainText())
            return True
        return False
        
    def showWarningDialog(self,message,informative_text=None):
        msg=QMessageBox()
        msg.setModal(True)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Message")
        msg.setText(f"<b>{message}<b>")
        msg.setInformativeText(informative_text)
        msg.exec_()
    
    def InsertNewTab(self):
        self.tab = QWidget()
        self.tab.setObjectName("tab1")
        tabName="Untitled_"+str(self.tabCounter)
        self.ui.tabWidget.addTab(self.tab, tabName)
        self.tabCounter+=1
        self.ui.tabWidget.setCurrentWidget(self.tab)
        self.TabDictionary[self.ui.tabWidget.currentIndex()]=[tabName,None]
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.textEditBody = QtWidgets.QTextEdit(self.tab)
        self.textEditBody.setFocus(True)
        self.gridLayout.addWidget(self.textEditBody, 0, 0, 1, 1)
    
    def updateTabOnFileOperation(self,filePath,fileName):
        self.TabDictionary[self.ui.tabWidget.currentIndex()]=[0,0]
        self.TabDictionary[self.ui.tabWidget.currentIndex()][0]=fileName
        self.TabDictionary[self.ui.tabWidget.currentIndex()][1]=filePath
        self.ui.tabWidget.setTabText(self.ui.tabWidget.currentIndex(),fileName)
        
    def CurrentTabNameUpdate(self):        
        CurrentTab=self.ui.tabWidget.currentWidget()
        CurrentTab.findChild(QTextEdit).textChanged.connect(self.TabFileEdited)
        
    def TabFileEdited(self):
        index=self.ui.tabWidget.currentIndex()
        if self.TabDictionary[index][0][0]=='*':
            return
        self.TabDictionary[index][0]="*"+self.TabDictionary[index][0]
        self.ui.tabWidget.setTabText(index,self.TabDictionary[index][0])
        
    def removeTab(self,index):
        def masbtn(i):
            if i.text()=="Discard":
                rmtab()
            elif i.text()=="Save":
                self.fileDialogBoxSaveFile()
            
        def rmtab():
            self.ui.tabWidget.removeTab(index)
            del self.TabDictionary[index]
            if self.ui.tabWidget.count()==0:
                self.InsertNewTab()
            
        try:
            if self.TabDictionary[index][0][0]=='*':
                filename=self.TabDictionary[index][0].strip("*")
                msg=QMessageBox()
                msg.setModal(True)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Message")
                msg.setText(f"<b>'{filename}' Changed.<b>")
                msg.setInformativeText("Do you want to save your changes?")
                msg.setStandardButtons(QMessageBox.Save|QMessageBox.Cancel|QMessageBox.Discard)
                msg.setDefaultButton(QMessageBox.Save)
                msg.buttonClicked.connect(masbtn)
                msg.exec_()
            else:
                rmtab()
        except:
            pass
def main(system_string):
    App=QApplication(system_string)
    window=Window()
    window.show()
    sys.exit(App.exec())

main(sys.argv)
