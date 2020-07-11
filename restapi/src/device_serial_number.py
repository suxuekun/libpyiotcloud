# pip install siphash-cffi
from siphash import siphash_64,half_siphash_32
from rest_api_config import config



class device_serial_number:

    def __init__(self):

        self.key = config.CONFIG_HASHKEY_SERIAL_DEVICE
        if len(self.key):
            self.key_for_hash = []
            for i in range(0, len(self.key), 2):
                val = int("0x{}".format(self.key[i: i+2]), 16)
                self.key_for_hash.append(val)

    def _get_siphash(self, uuid, key_for_hash):

        output = siphash_64(bytes(key_for_hash)[:], bytes(uuid[:-1])).hex().upper()
        output_siphash = ''
        for i in range(len(output)-1, -1, -2):
            output_siphash += output[i-1:i+1].upper()
        value = int(output_siphash, 16)

        return value

    def _get_halfsiphash(self, uuid, key_for_hash):

        output = half_siphash_32(bytes(key_for_hash)[:8], bytes(uuid[:-1])).hex().upper()
        output_halfsiphash = ''
        for i in range(len(output)-1, -1, -2):
            output_halfsiphash += output[i-1:i+1].upper()
        value = int(output_halfsiphash, 16)

        return value

    def compute_by_uuid(self, uuid):

        try:
            if isinstance(uuid, str):
                uuid_list = list(uuid.encode("utf-8"))
                return self._get_siphash(uuid_list, self.key_for_hash), self._get_halfsiphash(uuid_list, self.key_for_hash)
            return self._get_siphash(uuid, self.key_for_hash), self._get_halfsiphash(uuid, self.key_for_hash)
        except Exception as e:
            print(e)

        return 0, 0