import json



FOLDER = "devices/"
MASTER_LIST = "master_list.json"
CLASS_ID = "class_id.json"

# Sample files
SAMPLE_GW_DESC = "GW.json"
SAMPLE_LDS_REG = "Reg.json"



class device_client_type:
	ACTUATOR = 0
	SENSOR   = 1


class device_client:

	def __init__(self):
		self.master_list = None
		self.class_id = None
		self.gw_desc = None
		self.lds_reg = None
		self.lds_reg_file = None
		pass


	def _readfile(self, filename):
		try:
			f = open(FOLDER + filename, "r")
			json_obj = f.read()
			f.close()
			json_obj = json.loads(json_obj)
		except Exception as e:
			#print(e)
			return None
		return json_obj

	def _writefile(self, filename, json_obj):
		print()
		try:
			f = open(FOLDER + filename, "w")
			f.write(json_obj)
			f.close()
		except Exception as e:
			print(e)
			return False
		return True

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


	def initialize(self, lds_filename=None):
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

		self.gw_desc = self._readfile(SAMPLE_GW_DESC)
		if lds_filename is None:
			self.lds_reg = self._readfile(SAMPLE_LDS_REG)
			self.lds_reg_file = SAMPLE_LDS_REG
		else:
			self.lds_reg = self._readfile(lds_filename)
			if self.lds_reg is None:
				self.lds_reg = self._readfile(SAMPLE_LDS_REG)
				self.lds_reg_file = SAMPLE_LDS_REG
			else:
				self.lds_reg_file = lds_filename
		#self.test()


	def get_gw_desc(self):
		if self.gw_desc is None:
			return None
		return self.gw_desc

	def get_lds_reg(self):
		if self.lds_reg is None:
			return None
		return self.lds_reg["LDS"]

	def save_lds_reg(self, filename, json_obj):
		self._writefile(filename, json_obj)

	def iscustom_lds_reg(self):
		return self.lds_reg_file == SAMPLE_LDS_REG

	def get_ldsu_reg_from_lds_reg_template(self, obj):
		lds_reg = self._readfile(SAMPLE_LDS_REG)
		if lds_reg is None:
			return None
		for item in lds_reg["LDS"]:
			if int(item["OBJ"]) == int(obj):
				return item
		return None


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

	# get address - "C", "%", "LUX", " "
	def get_objidx_address(self, descriptor):
		return descriptor["ADDRESS"]

	# get accuracy - decimal place
	def get_objidx_accuracy(self, descriptor, mode=0):
		if descriptor.get("MODE") is not None:
			return descriptor["MODE"][mode]["Accuracy"]
		return descriptor["ACCURACY"]

	# get minmax
	def get_objidx_minmax(self, descriptor, mode=0):
		if descriptor.get("MODE") is not None:
			return descriptor["MODE"][mode]["Min"], descriptor["MODE"][mode]["Max"]
		return descriptor["MIN"], descriptor["MAX"]

	# get modes
	def get_objidx_modes(self, descriptor):
		if descriptor.get("MODE") is not None:
			return descriptor["MODE"]
		return None


	def test(self):

		objs = ["32768", "32769", "32770", "32771", "32772", "32773"]
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
					print("ADDRESS  {}".format(self.get_objidx_address(descriptor)))
					print()
			print()
			print()


#g_device_client = device_client()
#g_device_client.initialize()
#g_device_client.test()
