# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TerraqubeCloud
                                 A QGIS plugin
 This plugin provides access to hyperspectral images from Terraqube Cloud.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-02-10
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Terraqube S.L.
        email                : arnau@terraqube.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem, QHeaderView

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .terraqube_cloud_dialog import TerraqubeCloudDialog
import os.path
import requests
import json

class Cloudqube:
    def __init__(self, server):
        self.server = server
        self.token = None

    def get_url(self, url):
        return "{0}/terraqube/cloudqube/1.0.0/{1}".format(self.server, url)
     
    def post(self, url, data={}):
        url = self.get_url(url)
        headers = {
            "accepts": "application/json",
            "Content-type": "application/json"
        }
        if self.token:
            headers["Authorization"] = "Bearer {0}".format(self.token)
        return requests.post(
            url,
            data=json.dumps(data),
            headers=headers)

    def get(self, url, data={}):
        url = self.get_url(url)
        headers = {
            "accepts": "application/json",
            "Content-type": "application/json"
        }
        if self.token:
            headers["Authorization"] = "Bearer {0}".format(self.token)
        return requests.get(
            url,
            params=data,
            headers=headers)

    def login_user(self, username, password):
        """Login user to Terraqube Cloud using username and password."""
        response = self.post("user/login", {"username": username, "password": password})
        if (response.ok):
            data = json.loads(response.content)
            self.token = data['access_token']
        else:
            response.raise_for_status()
            
    def get_hyperqubes(self):
        """Get list of hyperqubes for current user."""
        response = self.get("hiperqubes")
        if (response.ok):
            return json.loads(response.content)
        else:
            response.raise_for_status()

class TerraqubeCloud:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TerraqubeCloud_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Terraqube Hyperspectral Cloud')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TerraqubeCloud', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/terraqube_cloud/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Terraqube Hyperspectral Cloud'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Terraqube Hyperspectral Cloud'),
                action)
            self.iface.removeToolBarIcon(action)
    
    def initHyperqubeTable(self, hyperqubes):
        """Initializes the hyperqube table with the hyperqubes retrieved from the server."""
        self.dlg.hyperqubeTable.clearContents()
        self.dlg.hyperqubeTable.setRowCount(len(hyperqubes))
        i = 0
        for hyperqube in hyperqubes:
            self.dlg.hyperqubeTable.setItem(i, 0, QTableWidgetItem(hyperqube['name']))
            self.dlg.hyperqubeTable.setItem(i, 1, QTableWidgetItem(hyperqube['captureDate']))
            self.dlg.hyperqubeTable.setItem(i, 2, QTableWidgetItem(hyperqube['uploadDate']))
            i = i + 1

    def sign_in(self):
        """Signs in a user to Terraqube Cloud."""
        server = self.dlg.serverInput.text().strip()
        username = self.dlg.usernameInput.text().strip()
        password = self.dlg.passwordInput.text().strip()
        if (server and username and password):
            self.cloudqube = Cloudqube(server)
            try:
                self.cloudqube.login_user(username, password)
                self.iface.messageBar().pushSuccess("Success", "Signed in Terraqube Cloud!")
                hyperqubes = self.cloudqube.get_hyperqubes()
                self.initHyperqubeTable(hyperqubes)
                self.dlg.terraqubeTab.setCurrentWidget(self.dlg.hyperqubes)
            except Exception as err:
                self.iface.messageBar().pushCritical("Failure", "Couldn't sign in to Terraqube Cloud: {0}".format(err))

    def select_hyperqube(self, row, col):
        """Action to execute when a hyperqube is selected."""
        self.iface.messageBar().pushSuccess("Success", "Hyperqube clicked: {0} {1}".format(row,col))

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = TerraqubeCloudDialog()
            self.dlg.signInButton.clicked.connect(self.sign_in)
            self.dlg.hyperqubeTable.setColumnCount(3)
            self.dlg.hyperqubeTable.setHorizontalHeaderLabels(['Name', 'Capture Date', 'Upload Date'])
            self.dlg.hyperqubeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.dlg.hyperqubeTable.cellDoubleClicked.connect(self.select_hyperqube)

        

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
