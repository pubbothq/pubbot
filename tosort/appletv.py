
import requests
import uuid
import hashlib

# http://nto.github.com/AirPlay.html


class AirPlay(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.session_id = str(uuid.uuid1())
        self.session = requests.Session()

    def photo(self, image_path):
        data = open(image_path, 'rb').read()
        data_sha = str(uuid.UUID(hashlib.sha1(data).hexdigest()[:32]))

        headers = {
            "X-Apple-AssetKey": data_sha,
            # "X-Apple-AssetAction": "displayCached",
            "X-Apple-Session-ID": self.session_id,
            "User-Agent": "MediaControl/1.0",
            }

        r = self.session.put("http://%s:%s/photo" % (self.host, self.port),
            headers=headers, data=data)

        return r.text


if __name__ == "__main__":
    a = AirPlay("192.168.254.2", 7000)
    print a.photo("kitten.jpg")
    import time
    time.sleep(10)


