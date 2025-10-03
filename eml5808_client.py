# robot_client.py
import json, socket

class RoboHubClient:
    def __init__(self, host="192.168.8.113", port=5555, timeout=2.0):
        self.host, self.port = host, port
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.file = self.sock.makefile("rwb", buffering=0)
        self._hello()

    def _send(self, obj):
        line = (json.dumps(obj) + "\n").encode("utf-8")
        self.file.write(line)

    def _read(self):
        line = self.file.readline()
        if not line:
            raise ConnectionError("server closed")
        return json.loads(line.decode("utf-8").strip())

    def _hello(self):
        self._send({"type":"hello","role":"user"})
        _ = self._read()  # {"type":"hello_ok","role":"user"}

    # ========== Public API ==========
    def list(self):
        self._send({"type":"list"})
        resp = self._read()
        if resp.get("type")=="list":
            return resp.get("robots", [])
        raise RuntimeError(resp)

    def connect(self, robot_id):
        self._send({"type":"connect","robot_id":robot_id})
        resp = self._read()
        if resp.get("type")=="ok":
            return True
        return False

    def move(self, robot_id, velocity, angular_velocity):
        self._send({"type":"move","robot_id":robot_id,"v":velocity,"w":angular_velocity})
        resp = self._read()
        if resp.get("type")=="ok":
            return True
        return False

    def currentPose(self, robot_id):
        self._send({"type":"get_pose","robot_id":robot_id})
        resp = self._read()
        if resp.get("type")=="pose":
            return resp["x"], resp["y"], resp["theta"]
        raise RuntimeError(resp)

    # Cleanup
    def close(self):
        try:
            self.file.close()
        finally:
            self.sock.close()
