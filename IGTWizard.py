import os
import unittest
import os.path
import platform
from __main__ import vtk, qt, ctk, slicer

#
# IGTWizard
#
class IGTWizard:
  def __init__(self, parent):
    parent.title = "IGTWizard" # TODO make this more human readable by adding spaces
    parent.categories = ["IGT"]
    parent.dependencies = []
    parent.contributors = ["Junichi Tokuda (Brigham and Women's Hospital) and Atsushi Yamada (Shiga University of Medical Science)"]
    parent.helpText = """
    This module only binds the existing modules that are required for given clinical applications, and allows the users to go through those modules by simply clicking the navigation buttons. The details are in <a href=http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/IGTWizard>the online documentation</a>.
    """
    parent.acknowledgementText = """
    This work was partially funded by NIH (R01 CA111288, P41 EB015898, U54 EB005149, R01 CA138586), CIMIT and Biomedical Innovation Center at Shiga University of Medical Science in Japan.
    """ 
    self.parent = parent

    # Add this test to the SelfTest module's list for discovery when the module
    # is created.  Since this module may be discovered before SelfTests itself,
    # create the list if it doesn't already exist.
    try:
      slicer.selfTests
    except AttributeError:
      slicer.selfTests = {}
    slicer.selfTests['IGTWizard'] = self.runTest

  def runTest(self):
    tester = IGTWizardTest()
    tester.runTest()

#
# qIGTWizardWidget
#
class ModuleListProperty:
  module = ''
  label = ''
  number = ''

class ModuleButtonProperty:
  module = ''
  label = ''
  handler = None
  button = None

class IGTWizardWidget:

  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # if this import is at top of the source, the loading could not work well.
    #import glob 
    # Instantiate and connect widgets ...

    #
    # Reload and Test area
    #
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload && Test"
    reloadCollapsibleButton.collapsed = True
    #self.layout.addWidget(reloadCollapsibleButton)
    ##reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "IGTWizard Reload"
    #reloadFormLayout.addWidget(self.reloadButton)
    ##self.reloadButton.connect('clicked()', self.onReload)

    # reload and test button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadAndTestButton = qt.QPushButton("Reload and Test")
    self.reloadAndTestButton.toolTip = "Reload this module and then run the self tests."
    #reloadFormLayout.addWidget(self.reloadAndTestButton)
    ##self.reloadAndTestButton.connect('clicked()', self.onReloadAndTest)

    #
    # Parameters Area
    #
    self.configurationCollapsibleButton = ctk.ctkCollapsibleButton()
    self.configurationCollapsibleButton.text = "Setup"
    self.configurationCollapsibleButton.collapsed = False
    self.configurationList = self.configurationCollapsibleButton
    self.layout.addWidget(self.configurationCollapsibleButton)
    # Layout within the collapsible button
    self.configurationFormLayout = qt.QFormLayout(self.configurationCollapsibleButton)

    self.aboutItemListFrame = qt.QFrame()
    self.aboutItemLayout = qt.QHBoxLayout()
    self.aboutItemListFrame.setLayout(self.aboutItemLayout)
    self.configurationFormLayout.addRow("Item List:", self.aboutItemListFrame)

    self.aboutOperationFrame = qt.QFrame()
    self.aboutOperationLayout = qt.QHBoxLayout()
    self.aboutOperationFrame.setLayout(self.aboutOperationLayout)
    self.configurationFormLayout.addRow("Operation:", self.aboutOperationFrame)

    self.aboutPanelFrame = qt.QFrame()
    self.aboutPanelLayout = qt.QHBoxLayout()
    self.aboutPanelFrame.setLayout(self.aboutPanelLayout)
    self.configurationFormLayout.addRow("Wizard Panel:", self.aboutPanelFrame)

    # Load File button
    self.fileReadButton = qt.QPushButton("Load")
    self.aboutItemListFrame.layout().addWidget(self.fileReadButton)
    self.fileReadButton.connect('clicked()', self.onLoad)

    # Save Extension List button
    self.saveExtensionListButton = qt.QPushButton("Save")
    self.saveExtensionListButton.enabled = False
    self.aboutItemListFrame.layout().addWidget(self.saveExtensionListButton)
    self.saveExtensionListButton.connect('clicked()', self.onSaveExtensionListButton)

    # Apply List button
    self.applyListButton = qt.QPushButton("Apply")
    self.applyListButton.enabled = False
    self.aboutPanelFrame.layout().addWidget(self.applyListButton)
    self.applyListButton.connect('clicked()', self.onApplyListButton)

    # Clear All button
    self.clearButton = qt.QPushButton("Reset")
    self.clearButton.enabled = False
    self.aboutPanelFrame.layout().addWidget(self.clearButton)
    self.clearButton.connect('clicked()', self.clearAllButtons)

    # Plus Extension List button
    self.plusButton = qt.QPushButton("+")
    self.plusButton.enabled = True
    self.aboutOperationFrame.layout().addWidget(self.plusButton)
    self.plusButton.connect('clicked()', self.onPlusButton)

    # Remove Extension List button
    self.removeButton = qt.QPushButton("-")
    self.removeButton.enabled = False
    self.aboutOperationFrame.layout().addWidget(self.removeButton)
    self.removeButton.connect('clicked()', self.onRemoveButton)

    # Wizard title edit box
    self.wizardTitleCollapsibleButton = ctk.ctkCollapsibleButton()
    self.wizardTitleCollapsibleButton.text = "Title"
    self.wizardTitleCollapsibleButton.collapsed = False
    self.wizardTitleList = self.wizardTitleCollapsibleButton
    self.layout.addWidget(self.wizardTitleCollapsibleButton)
    # Layout within the collapsible button
    self.wizardTitleFormLayout = qt.QFormLayout(self.wizardTitleCollapsibleButton)

    self.wizardTitleTextBox = qt.QLineEdit()
    self.wizardTitleTextBox.enabled = True
    self.wizardTitleTextBox.text = "IGT Wizard"
    self.wizardTitleFormLayout.addRow("Wizard Title:", self.wizardTitleTextBox)
    self.wizardTitleTextBox.connect('textEdited(QString)', self.editedWizardTitle)

    self.extensionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.extensionCollapsibleButton.text = "Item List"
    self.extensionCollapsibleButton.collapsed = True
    self.extensionCollapsibleButton.enabled = False
    self.extensionList = self.extensionCollapsibleButton
    self.layout.addWidget(self.extensionCollapsibleButton)
    # Layout within the collapsible button
    self.extensionFormLayout = qt.QFormLayout(self.extensionCollapsibleButton)

    #
    # Dock Panel
    #
    self.createDockPanel()

    # Add vertical spacer
    self.layout.addStretch(1)

    self.extensionSelector = {}
    self.installedExtensionName = {}
    self.selectedItem = {}

    self.currentModuleId = 0
    self.numberOfModule = 0
    self.numberOfExtention = 0
    self.numberOfExtentionList = 0
    self.loadFileFlag = 0
    self.numberOfLabelText = 15
    self.itemsOnOneLine = 3

    self.makeExtensionList()

  def makeExtensionList(self):
    import glob

    self.scriptPath = __file__

    pathFlag = 0
    appPath = ""
    for i in xrange(0, 500):
      if(self.scriptPath.find('/bin', 0, i) != -1 and pathFlag == 0):
        appPath = self.scriptPath[:i-4]
        pathFlag = 1

    # check platform
    platformName = platform.system()
    print("platform =")
    print(platformName)

    if(platformName == 'Darwin'):
      loadableModulePath = appPath + "/lib/Slicer*/qt-loadable-modules/*Module.dylib" 
      cliModulePath = appPath + "/lib/Slicer*/cli-modules/*Lib.dylib"
    if(platformName == 'Windows'):
      loadableModulePath = appPath + "/lib/Slicer*/qt-loadable-modules/*Module.dll" 
      cliModulePath = appPath + "/lib/Slicer*/cli-modules/*Lib.dll"
    if(platformName == 'Linux'):
      loadableModulePath = appPath + "/lib/Slicer*/qt-loadable-modules/*Module.so" 
      cliModulePath = appPath + "/lib/Slicer*/cli-modules/*Lib.so"

    scriptedModulePath = appPath + "/lib/Slicer*/qt-scripted-modules/*.py"
    
    filesForQtLoadableModule = glob.glob(loadableModulePath)
    filesForQtScriptedModule = glob.glob(scriptedModulePath) 
    filesForCliModule = glob.glob(cliModulePath)

    settings = slicer.app.revisionUserSettings()
    modulesAdditionalPaths = settings.value("Modules/AdditionalPaths") 
    # See ExtensionWizard.py and qSlicerSettingsModulesPanel.cxx

    for file in modulesAdditionalPaths:

      if(platformName == 'Darwin'):
        loadableModulePathSource = file + "/*Module.dylib"
        cliModulePathSource = file + "/*Lib.dylib"
      if(platformName == 'Windows'):
        loadableModulePathSource = file + "/*Module.dll"
        cliModulePathSource = file + "/*Lib.dll"
      if(platformName == 'Linux'):
        loadableModulePathSource = file + "/*Module.so"
        cliModulePathSource = file + "/*Lib.so"

      pyPathSource = file + "/*.py"

      loadableModulePath = glob.glob(loadableModulePathSource)
      cliModulePath = glob.glob(cliModulePathSource)
      pyPath = glob.glob(pyPathSource)

      if loadableModulePath:
        filesForQtLoadableModule += loadableModulePath
      if cliModulePath:
        filesForCliModule += cliModulePath
      if pyPath:
        filesForQtScriptedModule += pyPath

    tmpItemList = {}

    for file in filesForQtLoadableModule:
      if(platformName == 'Darwin'):
        editFileTmp = file.replace('Module.dylib','')
        editFile = editFileTmp.replace('libqSlicer','')
        slashLocation = editFile.rfind('/')
      if(platformName == 'Windows'):
        editFileTmp = file.replace('Module.dll','')
        editFile = editFileTmp.replace('qSlicer','')
        slashLocation = editFile.rfind('\\')
      if(platformName == 'Linux'):
        editFileTmp = file.replace('Module.so','')
        editFile = editFileTmp.replace('libqSlicer','')
        slashLocation = editFile.rfind('/')
      
      tmpItemList[self.numberOfExtention] = editFile[slashLocation+1:]
      self.numberOfExtention = self.numberOfExtention + 1

    for file in filesForQtScriptedModule:      
      editFile = file.replace('.py','')     
      if(platformName == 'Darwin'):
        slashLocation = editFile.rfind('/')
      if(platformName == 'Windows'):
        slashLocation = editFile.rfind('\\')
      if(platformName == 'Linux'):
        slashLocation = editFile.rfind('/')
      
      tmpItemList[self.numberOfExtention] = editFile[slashLocation+1:]
      self.numberOfExtention = self.numberOfExtention + 1

    for file in filesForCliModule:
      if(platformName == 'Darwin'):      
        editFileTmp = file.replace('Lib.dylib','')
        editFile = editFileTmp.replace('lib','')
        slashLocation = editFile.rfind('/')
      if(platformName == 'Windows'):
        editFile = file.replace('Lib.dll','')
        slashLocation = editFile.rfind('\\')
      if(platformName == 'Linux'):
        editFileTmp = file.replace('Lib.so','')
        editFile = editFileTmp.replace('lib','')
        slashLocation = editFile.rfind('/')

      tmpItemList[self.numberOfExtention] = editFile[slashLocation+1:]
      self.numberOfExtention = self.numberOfExtention + 1

    sortedList = {}
    sortedList = sorted(tmpItemList.items(), key=lambda x: x[1])
    for x in xrange(0,self.numberOfExtention):
      self.installedExtensionName[x] = sortedList[x][1] 

  def createDockPanel(self):
    self.modules = []

    self.dockPanel = qt.QDockWidget('IGT Wizard')
    self.dockPanel.windowTitle = self.wizardTitleTextBox.text
    self.dockPanel.setAllowedAreas(qt.Qt.LeftDockWidgetArea | qt.Qt.RightDockWidgetArea);

    self.dockFrame = qt.QFrame(self.dockPanel)
    self.dockFrame.setFrameStyle(qt.QFrame.NoFrame)
    self.dockLayout = qt.QVBoxLayout()

    ## Button Frame
    self.dockButtonFrame = qt.QFrame(self.dockFrame)
    self.dockButtonFrame.setFrameStyle(qt.QFrame.NoFrame)
    self.dockButtonLayout = qt.QHBoxLayout()
      
    self.dockButtonFrame.setLayout(self.dockButtonLayout)

    ## Wizard Frame
    self.dockWizardFrame = qt.QFrame(self.dockFrame)
    self.dockWizardFrame.setFrameStyle(qt.QFrame.NoFrame)
    self.dockWizardLayout = qt.QHBoxLayout()

    self.backButton = qt.QPushButton(" << ")
    self.backButton.enabled = False
    self.backButton.connect('clicked()', self.onBack)
    self.nextButton = qt.QPushButton(" >> ")
    self.nextButton.enabled = False
    self.nextButton.connect('clicked()', self.onNext)
    self.IGTWizardButton = qt.QPushButton("IGTWizard")
    self.IGTWizardButton.enabled = False
    self.IGTWizardButton.connect('clicked()', self.onIGTWizard)    

    self.dockWizardLayout.addWidget(self.backButton)
    self.dockWizardLayout.addWidget(self.nextButton)
    self.dockWizardLayout.addWidget(self.IGTWizardButton)
    self.dockWizardFrame.setLayout(self.dockWizardLayout)
    self.dockLayout.addWidget(self.dockWizardFrame)

    ## Set frame to the dock panel
    self.dockFrame.setLayout(self.dockLayout)
    self.dockPanel.setWidget(self.dockFrame)

    self.dockButtonFrame.show()
    self.dockWizardFrame.show()
    mw = slicer.util.mainWindow()
    mw.addDockWidget(qt.Qt.LeftDockWidgetArea, self.dockPanel)
    self.dockFrame.show()    

  def cleanup(self):
    pass

  def enter(self):
    pass

  def editedWizardTitle(self, inputText):
    self.dockPanel.windowTitle = inputText

  def onModuleChange(self, moduleId):
    print 'Change module to %s' % self.modules[moduleId].module
    slicer.util.selectModule(self.modules[moduleId].module)
    self.modules[self.currentModuleId].button.setChecked(False)
    self.modules[moduleId].button.setChecked(True)
    self.currentModuleId = moduleId
    self.IGTWizardButton.enabled = True    

  def clearAllButtons(self):
    self.numberOfModule = 0
    self.clearButton.enabled = False

    #Delete IGT Wizard Panel
    self.dockPanel.close()

    #Cretate IGT Wizard Panel
    self.createDockPanel()

  def onPlusButton(self):
    # Extension selector
    self.extensionSelector[self.numberOfExtentionList] = qt.QComboBox()
    self.extensionSelector[self.numberOfExtentionList].enabled = True  
    self.extensionSelector[self.numberOfExtentionList].addItem("None")

    if(self.numberOfExtentionList == 0):
      self.extensionCollapsibleButton.collapsed = False
      self.extensionCollapsibleButton.enabled = True

    for i in range(self.numberOfExtention):
      self.extensionSelector[self.numberOfExtentionList].addItem(self.installedExtensionName[i])
      if(self.loadFileFlag == 1 and self.modules[self.numberOfModule].module == self.installedExtensionName[i]):
        self.extensionSelector[self.numberOfExtentionList].setCurrentIndex(i+1) # the item 'None' requires i+1.

    self.extensionFormLayout.addWidget(self.extensionSelector[self.numberOfExtentionList])
    self.numberOfExtentionList = self.numberOfExtentionList + 1
    self.removeButton.enabled = True
    self.saveExtensionListButton.enabled = True
    self.applyListButton.enabled = True
    # Reset the current item
    self.currentModuleId = 0

  def onRemoveButton(self):
    self.numberOfExtentionList = self.numberOfExtentionList - 1
    # Reset the current item
    self.currentModuleId = 0

    self.extensionFormLayout.removeWidget(self.extensionSelector[self.numberOfExtentionList])
    if(self.numberOfExtentionList == 0):
      self.removeButton.enabled = False
      self.extensionCollapsibleButton.collapsed = True
      self.extensionCollapsibleButton.enabled = False
      self.saveExtensionListButton.enabled = False
      self.applyListButton.enabled = False

  def clearItemList(self):
    for i in xrange(0,self.numberOfExtentionList):
      self.onRemoveButton()

  def onSaveExtensionListButton(self):
    data = {}
    data = self.makeFile()

    fileName = qt.QFileDialog.getSaveFileName()
    f = open(fileName, 'w')
    f.write(data)
    f.close()
    
  def makeFile(self):
    data = {}

    data = "<items>\n"
    data += "<title>"
    data += self.dockPanel.windowTitle
    data += "</title>\n"
    data += "# module name and label name\n"

    for x in xrange(0,self.numberOfExtentionList):
      data += "<item>"
      data += self.extensionSelector[x].currentText
      data += ","
      data += self.extensionSelector[x].currentText[0:self.numberOfLabelText]
      data += "</item>\n"

    data += "</items>"

    return data    

  def makeButtons(self):
    id = 0
    bthProp = 0

    for btnProp in self.modules:
      btnProp.button = qt.QPushButton(btnProp.label)
      btnProp.button.setCheckable ( True )
      # NOTE: we cannot use lambda for slot here, because it treats 'id' as a valuable
      #       see http://math.andrej.com/2009/04/09/pythons-lambda-is-broken/
      def f(id=id): return self.onModuleChange(id)
      btnProp.handler = f;
      #print('function =')
      #print btnProp.handler
      print 'Change module to %s' % self.modules[id].module
      btnProp.button.connect('clicked()', btnProp.handler)
      self.dockButtonLayout.addWidget(btnProp.button)

      if((id+1) % self.itemsOnOneLine == 0 and id != 0): # Change the row
        self.dockLayout.addWidget(self.dockButtonFrame)
        self.dockButtonLayout = qt.QHBoxLayout()
        self.dockButtonFrame = qt.QFrame(self.dockFrame)
        self.dockButtonFrame.setFrameStyle(qt.QFrame.NoFrame)
        self.dockButtonFrame.setLayout(self.dockButtonLayout)
      id = id + 1

    self.dockLayout.addWidget(self.dockButtonFrame)    
    self.dockLayout.removeWidget(self.dockWizardFrame)
    self.dockLayout.addWidget(self.dockWizardFrame)

    self.backButton.enabled = True
    self.nextButton.enabled = True
    self.clearButton.enabled = True

  def onApplyListButton(self):
    self.loadFileFlag = 1
    self.clearAllButtons() # clear self.module
    
    self.wizardTitleTextBox.text = self.dockPanel.windowTitle  

    for x in xrange(0,self.numberOfExtentionList):
      moduleName = self.extensionSelector[x].currentText
      label = self.extensionSelector[x].currentText[0:self.numberOfLabelText]
      p = ModuleButtonProperty()
      p.module = moduleName
      p.label = label[0:self.numberOfLabelText]
      self.modules.append(p)   

    self.makeButtons()

    self.loadFileFlag = 0

  def onLoad(self):
    import os.path
    self.loadFileFlag = 1

    fileName = qt.QFileDialog.getOpenFileName()
    #print(fileName)
    if(fileName != ""):
      self.clearItemList()
      f = open(fileName, "rb")

    if(fileName != ""):
      l = 1
      self.clearAllButtons() # clear self.module

      while l:
        #print l,
        l = f.readline()

        if(l.find('#') == -1): # If the line is not a comment one...

          splitText = l.split(',')
          number = len(splitText)

          if((l.find("<item>") >= 0 or l.find("<Item>") >= 0) and number >= 2): # If the line has ',', the code recognizes an item. 
            #print(number)
            #print(splitText[0])
            #print(splitText[1])

            splitText[0] = splitText[0].replace('<item>', '').replace('<Item>', '').rstrip().lstrip()
            splitText[1] = splitText[1].replace('</item>', '').replace('</Item>', '').rstrip().lstrip()

            moduleName = splitText[0]
            label = splitText[1]
            p = ModuleButtonProperty()
            p.module = moduleName
            p.label = label[0:self.numberOfLabelText]
            self.modules.append(p)   
            self.onPlusButton()
            self.numberOfModule = self.numberOfModule + 1          

          elif(l.find("<title>") >= 0 or l.find("<Title>") >= 0):
            l = l.replace('<title>', '').replace('<Title>', '').replace('</title>', '').replace('</Title>', '').rstrip().lstrip()
            if not l:
              l = "IGT Wizard"
            self.dockPanel.windowTitle = l
            self.wizardTitleTextBox.text = l
            #print("title line is...")
            #print l
    
      f.close()

      self.makeButtons()

    self.loadFileFlag = 0

  def onBack(self):
    n = len(self.modules)
    next = (self.currentModuleId -1 + n) % n
    self.onModuleChange(next)
    self.IGTWizardButton.enabled = True

  def onNext(self):
    n = len(self.modules)
    next = (self.currentModuleId + 1) % n
    self.onModuleChange(next)
    self.IGTWizardButton.enabled = True

  def onIGTWizard(self):
    slicer.util.selectModule("IGTWizard")
    self.modules[self.currentModuleId].button.setChecked(False)
    self.IGTWizardButton.enabled = False

  def onReload(self,moduleName="IGTWizard"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

    #Delete IGT Wizard Pane
    self.dockPanel.close()

    widgetName = moduleName + "Widget"
    # reload the source code
    # - set source file path
    # - load the module to the global space
    filePath = eval('slicer.modules.%s.path' % moduleName.lower())
    p = os.path.dirname(filePath)
    if not sys.path.__contains__(p):
      sys.path.insert(0,p)
    fp = open(filePath, "r")
    globals()[moduleName] = imp.load_module(
        moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
    fp.close()

    # rebuild the widget
    # - find and hide the existing widget
    # - create a new widget in the existing parent
    parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
    for child in parent.children():
      try:
        child.hide()
      except AttributeError:
        pass
    # Remove spacer items
    item = parent.layout().itemAt(0)
    while item:
      parent.layout().removeItem(item)
      item = parent.layout().itemAt(0)

    # delete the old widget instance
    if hasattr(globals()['slicer'].modules, widgetName):
      getattr(globals()['slicer'].modules, widgetName).cleanup()

    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()
    setattr(globals()['slicer'].modules, widgetName, globals()[widgetName.lower()])

  def onReloadAndTest(self,moduleName="IGTWizard"):
    try:
      self.onReload()
      evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
      tester = eval(evalString)
      tester.runTest()
    except Exception, e:
      import traceback
      traceback.print_exc()
      qt.QMessageBox.warning(slicer.util.mainWindow(), 
          "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")

#
# IGTWizardLogic
#
class IGTWizardLogic:
  def __init__(self):
    pass

class IGTWizardTest(unittest.TestCase):
  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_IGTWizard1()

  def test_IGTWizard1(self):
    self.delayDisplay('Test passed!')
