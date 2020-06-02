import json



FOLDER = "devices/"
MASTER_LIST = "master_list.json"
CLASS_ID = "class_id.json"



class device_client_type:
	ACTUATOR = 0
	SENSOR   = 1


class device_client:

	def __init__(self):
		self.master_list = None
		self.class_id = None
		pass


	def _readfile(self, filename):
		try:
			f = open(FOLDER + filename)
			json_obj = f.read()
			f.close()
			json_obj = json.loads(json_obj)
		except Exception as e:
			print(e)
			return None
		return json_obj

	def _print_json(self, json_object, label=None):
		json_formatted_str = json.dumps(json_object, indent=2)
		if label is None:
			#printf(json_formatted_str)
			lines = json_formatted_str.split("\n")
			for line in lines:
				print(line)
		else:
			print(label)
			print("")
			print(json_formatted_str)


	def initialize(self):
		self.master_list = self._readfile(MASTER_LIST)
		if self.master_list is None:
			print("Could not read file properly {}".format(MASTER_LIST))
			return

		for device in self.master_list["devices"]:
			device["val"] = self._readfile(device["file"])
			if device["val"] is None:
				print("Could not read file properly {}".format(device["file"]))
				return

		self.class_id = self._readfile(CLASS_ID)
		if self.class_id is None:
			print("Could not read file properly {}".format(CLASS_ID))
			return

		self.test()


	def get_obj(self, obj):
		for device in self.master_list["devices"]:
			if obj == device["obj"]:
				return device["val"]
		return None

	def get_obj_type(self, obj):
		if int(obj) >= 8000:
			return device_client_type.SENSOR
		return device_client_type.ACTUATOR

	def get_obj_numdevices(self, obj):
		if self.get_obj(obj):
			return len(self.get_obj(obj)["SNS"])
		return 0

	def get_objidx(self, obj, idx):
		if idx >= self.get_obj_numdevices(obj):
			return None
		return self.get_obj(obj)["SNS"][idx]



	# get class
	def get_objidx_class(self, descriptor):
		cls_int = int(descriptor["CLS"])
		for class_id in self.class_id["classes"]:
			if cls_int == int(class_id["AttributeID"], 16):
				return class_id["AttributeName"] 
		return None

	# get said - index
	def get_objidx_said(self, descriptor):
		return descriptor["SAID"]

	# get format - "integer", "float", "boolean"
	def get_objidx_format(self, descriptor):
		return descriptor["FORMAT"]

	# get type - "INPUT", "OUTPUT", "CLOCK"
	def get_objidx_type(self, descriptor):
		return descriptor["TYPE"].lower()

	# get unit - "C", "%", "LUX", " "
	def get_objidx_unit(self, descriptor):
		return descriptor["UNIT"]

	# get accuracy - decimal place
	def get_objidx_accuracy(self, descriptor, mode=0):
		if descriptor.get("MODE"):
			return descriptor["MODE"][mode]["Accuracy"]
		return descriptor["ACCURACY"]

	# get minmax
	def get_objidx_minmax(self, descriptor, mode=0):
		if descriptor.get("MODE"):
			return descriptor["MODE"][mode]["Min"], descriptor["MODE"][mode]["Max"]
		return descriptor["MIN"], descriptor["MAX"]


	def test(self):

		objs = ["32768", "32770"]
		#objs = ["1793", "32768", "32770"]

		print()
		for obj in objs:
			num = self.get_obj_numdevices(obj)

			print("ACT/SEN  {} {}".format(self.get_obj_type(obj), num))
			for x in range(num):
				print("{}    {}".format(obj, x))

				descriptor = self.get_objidx(obj, x)
				if descriptor:
					#print(self.get_objidx(obj, x))
					print("FORMAT   {}".format(self.get_objidx_format(descriptor)))
					print("TYPE     {}".format(self.get_objidx_type(descriptor)))
					print("UNIT     {}".format(self.get_objidx_unit(descriptor)))
					print("ACCURACY {}".format(self.get_objidx_accuracy(descriptor)))
					print("MINMAX   {}".format(self.get_objidx_minmax(descriptor)))
					print("CLASS    {}".format(self.get_objidx_class(descriptor)))
					print()
			print()
			print()


#g_device_client = device_client()
#g_device_client.initialize()
#g_device_client.test()
