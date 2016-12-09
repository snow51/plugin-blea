from bluepy import btle
import time
import logging
import globals
import binascii
import struct

class Smartplug():
	def __init__(self):
		self.name = 'smartplug'

	def isvalid(self,name,manuf=''):
		if name.lower().startswith("smp-b16-"):
			return True
			
	def parse(self,data):
		action={}
		action['present'] = 1
		return action
		
	def connect(self,mac):
		logging.debug('Connecting : '+str(mac) + ' with bluetooth ' + str(globals.IFACE_DEVICE))
		i=0
		while True:
			i = i + 1
			try:
				conn = Peripheral(mac,iface=globals.IFACE_DEVICE)
				break
			except Exception as err:
				if i >= 4 :
					return
		return conn
	
	def action(self,message):
		mac = message['device']['id']
		handle = message['command']['handle']
		value = message['command']['value']
		conn = self.connect(mac)
		arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
		conn.writeCharacteristic(int(handle,16),struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
		conn.disconnect()
		result = self.read(mac)
		return result
	
	def read(self,mac):
		result={}
		try:
			conn = self.connect(mac)
			logging.debug('Connected...')
			value = '0f050400000005ffff'
			arrayValue = [int('0x'+value[i:i+2],16) for i in range(0, len(value), 2)]
			svc = conn.getServiceByUUID('0000fff0-0000-1000-8000-00805f9b34fb')
			cmd_ch = svc.getCharacteristics('0000fff3-0000-1000-8000-00805f9b34fb')[0]
			delegate = NotificationDelegate()
			conn.setDelegate(delegate)
			conn.writeCharacteristic(0x2b,struct.pack('<%dB' % (len(arrayValue)), *arrayValue))
			state,power = datas.conn.wait_notif(0.5)
			result['power'] = power
			result['status'] = state
			result['id'] = mac
			conn.disconnect()
			logging.debug(str(result))
			return result
		except Exception,e:
			logging.error(str(e))
		return result
		
	class NotificationDelegate(btle.DefaultDelegate):
		def __init__(self):
			btle.DefaultDelegate.__init__(self)

		def handleNotification(self, cHandle, data):
			if bytes_data[0:3] == bytearray([0x0f, 0x0f, 0x04]):
				state = bytes_data[4] == 1
				power = int(binascii.hexlify(bytes_data[6:10]), 16) / 1000
				return state,power

globals.COMPATIBILITY.append(Smartplug)