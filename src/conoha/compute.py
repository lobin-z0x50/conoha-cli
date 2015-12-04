
from .api import API

class ComputeAPI(API):
	_serviceType = 'compute'

	def __init__(self, token, baseURIPrefix=None):
		super().__init__(token, baseURIPrefix)

class VMPlan(ComputeAPI):
	planId = None
	name = None
	disk = None
	ram = None
	vcpus = None

	def __init__(self, data):
		self.planId = data['id']
		self.name = data['name']
		self.disk = data['disk']
		self.ram = data['ram']
		self.vcpus = data['vcpus']

class VMPlanList(ComputeAPI):
	_flavors = None

	def __init__(self, token):
		super().__init__(token)
		path = 'flavors/detail'
		res = self._GET(path)
		self._flavors = res['flavors']

	def __iter__(self):
		for f in self._flavors:
			yield VMPlan(f)

class VMImage(ComputeAPI):
	imageId = None
	name = None
	minDisk = None
	minRam = None
	progress = None
	status = None
	created = None
	updated = None

	def __init__(self, data):
		self.imageId = data['id']
		self.name = data['name']
		self.minDisk = data['minDisk']
		self.minRam = data['minRam']
		self.progress = data['progress']
		self.status = data['status']
		self.created = data['created']
		self.updated = data['updated']

class VMImageList(ComputeAPI):
	_images = None

	def __init__(self, token):
		super().__init__(token)
		path = 'images/detail'
		res = self._GET(path)
		self._images = res['images']

	def __iter__(self):
		for i in self._images:
			yield VMImage(i)

class VMList(ComputeAPI):
	_servers = None

	def __init__(self, token):
		super().__init__(token)
		self.update()

	def __iter__(self):
		if self._servers is None:
			self.update()

		for v in self._servers:
			yield VM(self.token, v)

	def update(self):
		res = self._GET('servers/detail')
		self._servers = res['servers']

	def getServer(self, vmid=None, name=None):
		for vm in self:
			if (vmid and vm.vmid == vmid) or (name and vm.name == name):
				return vm

	def add(self, image, flavor, adminPass=None, keyName=None, name=None, securityGroupNames=None):
		data = {'server' : {
				'imageRef' : image,
				'flavorRef' : flavor,
				'metadata': {},
				}}
		if adminPass: data['server']['adminPass'] = adminPass
		if keyName: data['server']['key_name'] = keyName
		if name:
			data['server']['metadata']['instance_name_tag'] = name
		if securityGroupNames:
			data['server']['security_groups'] = []
			for name in securityGroupNames:
				data['server']['security_groups'].append({
					'name': name,
					})

		res = self._POST('servers', data)
		self._servers = None
		return res['server']['id']

	def delete(self, vmid):
		self._DELETE('servers/'+vmid, isDeserialize=False)
		self._servers = None

class VM(ComputeAPI):
	vmid = None
	flavorId = None
	hostId = None
	imageId = None
	tenantId = None
	name = None
	status = None
	created = None
	updated = None
	addressList = None
	securityGroupList = None

	def __init__(self, token, info):
		super().__init__(token, baseURIPrefix='servers/' + self.vmid)
		self.vmid = info['id']
		self.flavorId = info['flavor']['id']
		self.hostId = info['hostId']
		self.imageId = info['image']['id']
		self.tenantId = info['tenant_id']
		try:
			self.name = info['metadata']['instance_name_tag']
		except KeyError:
			self.name = info['name']
		self.status = info['status']
		self.created = info['created']
		self.updated = info['updated']
		self.status = info['status']
		self.created = info['created']
		self.updated = info['updated']
		self.addressList = info['addresses']
		self.securityGroupList = info['security_groups']

	def _action(self, actionName, actionValue=None):
		action = {actionName: actionValue}
		self._POST('action', action, isDeserialize=False)
	def start(self):
		self._action('os-start')
	def stop(self, force=False):
		if force:
			self._action('os-stop', {'force_shutdown': True})
		else:
			self._action('os-stop')
	def restart(self):
		self._action('reboot', {'type': 'SOFT'})
	def resize(self, flavorId):
		self._action('resize', {'flavorRef': flavorId})
	def confirmResize(self):
		self._action('confirmResize')
	def revertResize(self):
		self._action('revertResize')
	def getStatus(self):
		res = self._GET('')
		return res['server']['status']

class KeyList(ComputeAPI):
	_keys = None

	def __init__(self, token):
		super().__init__(token)
		self.update()

	def __iter__(self):
		if self._keys is None:
			self.update()

		for key in self._keys:
			yield Key(key)

	def update(self):
		res = self._GET('os-keypairs')
		self._keys = (keypair['keypair'] for keypair in res['keypairs'])

	def add(self, name, publicKey=None, publicKeyFile=None):
		"""
		publicKey が文字列なら、そのキーを使用
		publicKeyFile が文字列なら、そのキーを使用
		publicKey or publicKeyFile がfile likeオブジェクトなら、そのキーを使用
		publicKey is None ならば、新しいキーを作成。必ず返されるKey objectからprivateKeyを取得し、保存すること
		"""
		data = {'keypair':{'name': name}}
		keyString = None

		if type(publicKey) is str:
			keyString = publicKey
		elif type(publicKeyFile) is str:
			with open(publicKeyFile) as f:
				keyString = f.read()
		elif (publicKey or publicKeyFile) is not None:
			keyString = (publicKey or publicKeyFile).read()
		else:
			res = self._POST('os-keypairs', data=data)
			return Key(res['keypair'])

		data['keypair']['public_key'] = keyString
		res = self._POST('os-keypairs', data=data)
		self._keys = None
		return Key(res['keypair'])

	def delete(self, keyName):
		self._DELETE('os-keypairs/'+keyName, isDeserialize=False)
		self._keys = None

class Key(ComputeAPI):
	name = None
	fingerprint = None
	publicKey = None
	privateKey = None

	def __init__(self, info):
		self.name = info['name']
		self.fingerprint = info['fingerprint']
		self.publicKey = info['public_key']
		self.privateKey = info.get('private_key')

