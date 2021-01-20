# Shinobi Python Plugin
#
# Author: Frix
# https://shinobi.video/docs/api
#
"""
<plugin key="shinobi" name="Shinobi" author="Frix" version="0.2" wikilink="https://shinobi.video/docs/api">
    <description>
        <h2>Shinobi - Monitor Controller</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
			<li>Creates switches for each monitor configured on the Shinobi server</li>
			<li>Enables Domoticz to change the status of Shinobi monitors</li>
		</ul>
        <h4>Devices</h4>
        <ul style="list-style-type:square">
            <li>State - Selector switch to start/stop/restart Shinobi</li>
            <li>Monitor Function - Selector switch to change the Function State of a Monitor. Availible states are "Watch Only/Record/Off".</li>
            <li>Monitor Status - Switch to Disable or Enable the Monitor Function</li>
        </ul>
        <h3>Requirements</h3>
        <ul style="list-style-type:square">
			<li>Shinobi API must be enabled, please see the API documentation (Wiki URL) for how to enable the API</li>
			<li>URL Address must contain the complete URL including http:// or https://</li>
        </ul>
    </description>
	<params>
		<param field="Address" label="URL Address" width="250px" required="true" default="http://192.168.1.10:8080/"/>
		<param field="Username" label="Email" width="250px" required="false" default="admin@shinobi.com"/>
		<param field="Password" label="Password" width="250px" required="false"/>
		<param field="Mode6" label="Debug" width="75px">
			<options>
				<option label="True" value="Debug"/>
				<option label="False" value="Normal"  default="true" />
			</options>
		</param>
	</params>
</plugin>
"""
import Domoticz
import requests

class API:
	def __init__(self):
		self.retryCount = 2
		self.url = None
		self.username = None
		self.password = None
		self.session = False
		self.timeout = 2
		return

	def login(self):
		self.url = Parameters["Address"]
		self.username = Parameters["Username"]
		self.password = Parameters["Password"]

		try:
			data = {
				'machineID': "test",
				'mail': str(self.username),
				'pass': str(self.password),
				'function': "dash"
			}
			resp = requests.post(self.url + '?json=true', data=data)
			self.session = {"API_KEY": str(resp.json()['$user']['auth_token']), "GROUP_KEY": str(resp.json()['$user']['ke'])}
			Domoticz.Log("Logged in to " + self.url)
		except requests.exceptions.RequestException as e:
			Domoticz.Log("Failed to fetch an API key from " + self.url + "! Make sure the URL Address for Shinobi is correct.")
			Domoticz.Debug(e)
		finally:
			Domoticz.Debug("Logged in at " + self.url + ": "+str(self.session))


	#cmd = monitor, videos, monitorStates etc
	#params = MODE, MONITOR ID, TIME, ACTION etc 
	def call(self, cmd, params = ""):
		for i in range(self.retryCount):
			try:
				monitors = requests.get(str(self.url) + str(self.session['API_KEY']) + "/" + str(cmd) + "/" + str(self.session['GROUP_KEY']) + "/" + str(params), timeout=self.timeout)
				#Domoticz.Log(str(monitors.json()))
				return monitors.json()
			except requests.exceptions.RequestException as e:
				retries = self.retryCount - i
				Domoticz.Log("Failed to get " + str(cmd) + " at " + str(self.url))
				Domoticz.Debug("Exception: " + str(e))
				Domoticz.Log("Retrying with new connection. Try " + str(retries) + " of " + str(self.retryCount) + " times...")
				self.login()
				continue

class BasePlugin:
	enabled = False
	def __init__(self):
		self.api = API()
		self.lastPolled = 0
		self.pollInterval = 20
		return

	def onStart(self):
		Domoticz.Log("onStart called")
		Domoticz.Heartbeat(30)

		#Login to Shinobi
		self.api.login()

		#Get all existing monitors from Shinobi
		monitors = self.api.call("monitor")
		Domoticz.Debug("Number of found monitors: " + str(len(monitors)))

		#Create Devices for each monitor that was found
		if len(Devices) == 0:
			if (len(monitors) > 0):
				for idx, monitor in enumerate(monitors):
					idx += 1
					Id = monitor['mid']
					Name = monitor['name']
					Mode = monitor['mode']

					Options = {"LevelActions": "||","LevelNames": "Off|Watch Only|Record","LevelOffHidden": "True","SelectorStyle": "0"}
					Domoticz.Device(Name="Monitor " + str(Name),  Unit=int(idx), DeviceID=str(Id), TypeName="Selector Switch", Options=Options).Create()
					Domoticz.Log("Device Monitor Unit " + str(idx) + " " + str(Name) + " with DeviceID " + str(Id) + " was created.")

					Domoticz.Device(Name="Monitor " + str(Name),  Unit=int(idx+10), DeviceID=str(Id), TypeName="Switch", Switchtype=9, Options=Options).Create()
					Domoticz.Log("Device Monitor Unit " + str(idx+10) + " " + str(Name) + " with DeviceID " + str(Id) + " was created.")

					lvl = str(10)
					if Mode == "record":
						lvl = str(20)
					if Mode == "idle":
						lvl = str(0)
					Devices[idx].Update(1,lvl)


		if Parameters["Mode6"] == "Debug":
			Domoticz.Debugging(1)

	def onStop(self):
		Domoticz.Log("onStop called")

	def onConnect(self, Connection, Status, Description):
		Domoticz.Log("onConnect called")

	def onMessage(self, Connection, Data):
		Domoticz.Log("onMessage called")

	def onCommand(self, Unit, Command, Level, Hue):
		Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

		cmd = 'monitor'		
		mid = str(Devices[Unit].DeviceID)

		if Level == 0:
			params = mid+'/stop'
			self.api.call(cmd, params)
			Devices[Unit].Update(1,str(0))
		if Level == 10:
			params = mid+'/start'
			self.api.call(cmd, params)
			Devices[Unit].Update(1,str(10))
		if Level == 20:
			params = mid+'/record'
			self.api.call(cmd, params)
			Devices[Unit].Update(1,str(20))

	def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
		Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

	def onDisconnect(self, Connection):
		Domoticz.Log("onDisconnect called")

	def onHeartbeat(self):
		Domoticz.Log("onHeartbeat called")

		self.lastPolled = self.lastPolled + 1
		if self.lastPolled > self.pollInterval:
			self.lastPolled = 0
			#Maintain a connection
			self.api.login()
			#Retry to add devices if non exists
			if (len(Devices) == 0):
				Domoticz.Debug("No devices found! Retrying to add devices...")
				self.onStart()
				
global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Data):
    global _plugin
    _plugin.onNotification(Data)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

	# Generic helper functions
def DumpConfigToLog():
	for x in Parameters:
		if Parameters[x] != "":
			Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
	Domoticz.Debug("Device count: " + str(len(Devices)))
	for x in Devices:
		Domoticz.Debug("Device:		   " + str(x) + " - " + str(Devices[x]))
		Domoticz.Debug("Device ID:	   '" + str(Devices[x].ID) + "'")
		Domoticz.Debug("Device Name:	 '" + Devices[x].Name + "'")
		Domoticz.Debug("Device nValue:	" + str(Devices[x].nValue))
		Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
		Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
	return
