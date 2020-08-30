from typing import Optional

from cryptoxlib.exceptions import CryptoXLibException


class HitbtcException(CryptoXLibException):
	pass


class HitbtcRestException(HitbtcException):
	def __init__(self, status_code: int, body: Optional[dict]):
		super().__init__(f"Rest API exception: status [{status_code}], response [{body}]")

		self.status_code = status_code
		self.body = body