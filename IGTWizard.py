import os
import unittest
import copy
from __main__ import vtk, qt, ctk, slicer

#
# IGTWizard
#

class IGTWizard:
  def __init__(self, parent):
    parent.title = "IGTWizard" # TODO make this more human readable by adding spaces
    parent.categories = ["IGT"]
    parent.dependencies = []
    parent.contributors = ["Junichi Tokuda (BWH)"]
    parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    parent.acknowledgementText = """
    This file was developed by Junichi Tokuda and was partially funded by NIH (R01 CA111288, P41 EB015898, U54 EB005149, R01 CA138586) and CIMIT.
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

class ModuleButtonProperty:
  module = ''
  label = ''
  color = ''
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

    self.modules = []

    p = ModuleButtonProperty();
    p.module = 'Data'
    p.label = 'Data'
    p.color = 'Red'
    self.modules.append(p)

    p = ModuleButtonProperty()
    p.module = 'OpenIGTLinkIF'
    p.label = 'OpenIGTLink IF'
    p.color = 'Blue'
    self.modules.append(p)

    p = ModuleButtonProperty()
    p.module = 'Annotations'
    p.label = 'Annotations'
    p.color = 'Green'
    self.modules.append(p)    
    
    self.currentModule = 'Data'
    self.initialized = 0

  def setup(self):
    # Instantiate and connect widgets ...

    # reload button
    # (use this during development, but remove it when delivering
    #  your module to users)
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "IGTWizard Reload"
    self.layout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    self.dockPanel = qt.QDockWidget('IGT Wizard')
    self.dockPanel.setAllowedAreas(qt.Qt.LeftDockWidgetArea | qt.Qt.RightDockWidgetArea);
    self.dockFrame = qt.QFrame(self.dockPanel)
    self.dockFrame.setFrameStyle(qt.QFrame.NoFrame)
    self.dockLayout = qt.QHBoxLayout()

    for btnProp in self.modules:
      key = btnProp.module
      print "%s -- %s" % (key, btnProp.label)
      btnProp.button = qt.QPushButton(btnProp.label)
      btnProp.button.setCheckable ( True )
      # NOTE: we cannot use lambda for slot here, because it treats 'key' as a vaiilable
      #       see http://math.andrej.com/2009/04/09/pythons-lambda-is-broken/
      def f(key=key): return self.onModuleChange(key)
      btnProp.handler = f;
      btnProp.button.connect('clicked()', btnProp.handler)
      self.dockLayout.addWidget(btnProp.button)
      
    self.dockFrame.setLayout(self.dockLayout)
    self.dockPanel.setWidget(self.dockFrame)
    mw = slicer.util.mainWindow()
    mw.addDockWidget(qt.Qt.LeftDockWidgetArea, self.dockPanel)
    self.dockFrame.show()

    # Add vertical spacer
    self.layout.addStretch(1)

    #slicer.util.selectModule(self.currentModule)
    self.onModuleChange(self.currentModule)
    self.initialized = 1


  def enter(self):
    if self.initialized == 1:
      slicer.util.selectModule(self.currentModule)
    
  def onModuleChange(self, moduleName):
    print 'Change module to %s' % moduleName
    slicer.util.selectModule(moduleName)
    for btnProp in self.modules:
      key = btnProp.module
      if key != moduleName:
        btnProp.button.setChecked(False)
      else:
        btnProp.button.setChecked(True)

  def onReload(self,moduleName="IGTWizard"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    import imp, sys, os, slicer

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
    # create new widget inside existing parent
    globals()[widgetName.lower()] = eval(
        'globals()["%s"].%s(parent)' % (moduleName, widgetName))
    globals()[widgetName.lower()].setup()

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
