
# -*- coding: utf8 -*-
from urllib.request import Request, urlopen
import json
__ALL__ = 'API Tenant'.split()

class API:
	baseURI = None
	token = None

	def _getHeaders(self, h):
		headers={
				'Accept': 'application/json',
				}
		if self.token:
			headers['X-Auth-Token'] = self.token.getAuthToken()
		if h:
			headers.update(h)
		return headers

	def _GET(self, path, data=None, isDeserialize=True, baseURI=None, headers=None, method='GET'):
		if data:
			data = bytes(json.dumps(data), 'utf8')
		req = Request(
				url=(baseURI or self.baseURI)+path,
				headers=self._getHeaders(headers),
				method=method,
				data=data,
				)
		with urlopen(req) as res:
			resBin = res.read()
			if isDeserialize:
				return json.loads(str(resBin, 'utf8'))
			else:
				return resBin

	def _DELETE(self, *args, **nargs):
		return self._GET(*args, method='DELETE', **nargs)

	def _POST(self, path, data, *args, **nargs):
		return self._GET(path, data, *args, method='POST', **nargs)

	def _PUT(self, path, data, *args, **nargs):
		return self._GET(path, data, *args, method='PUT', **nargs)

class Token(API):
	baseURI = 'https://identity.tyo1.conoha.io'
	conf = None
	token = None
	tenantId = None

	def __init__(self, conf):
		self.conf = conf
		path = '/v2.0/tokens'
		data = { 'auth':{
			'passwordCredentials':{
				'username': conf.get('api', 'user'),
				'password': conf.get('api', 'passwd'),
				},
			}}
		self.tenantId = conf.get('api', 'tenant')
		if self.tenantId:
			data['auth']['passwordCredentials']['tenantId'] = tenantId
		res = self._POST(path, data)
		self.token = res['access']['token']

	def getTenantId(self):
		return self.tenantId
	def getAuthToken(self):
		return self.token['id']

