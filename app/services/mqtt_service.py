# app/services/mqtt_service.py
import json
import threading
import paho.mqtt.client as _mqtt

class MQTTService:
    """
    Service bao bọc paho-mqtt:
    - init_app(app): đọc config, set callback, chạy loop ở daemon thread
    - publish(topic, payload, qos=0, retain=False)
    - subscribe(topic, handler)  # handler: (topic:str, payload:str) -> None
    """
    def __init__(self):
        self.client: _mqtt.Client | None = None
        self._handlers: dict[str, list] = {}   # topic -> [handler,...]
        self._connected = False
        self._host = "localhost"
        self._port = 1883

    def init_app(self, app):
        self._host = app.config.get("MQTT_BROKER_URL", "localhost")
        self._port = int(app.config.get("MQTT_BROKER_PORT", 1883))

        self.client = _mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Chạy loop ở background (tránh chạy 2 lần khi debug auto-reload)
        if not app.config.get("MQTT_DISABLED", False):
            t = threading.Thread(target=self._loop, daemon=True)
            t.start()

    def _loop(self):
        assert self.client is not None
        # Thử reconnect mãi cho đến khi thành công
        while True:
            try:
                self.client.connect(self._host, self._port, 60)
                self.client.loop_forever()
            except Exception as e:
                print("MQTT reconnect after error:", e)
                import time; time.sleep(1)

    # ===== paho callbacks =====
    def _on_connect(self, client, userdata, flags, rc):
        self._connected = True
        print("MQTT connected:", rc)
        # Re-subscribe tất cả topic đã đăng ký
        for topic in self._handlers.keys():
            client.subscribe(topic)

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode(errors="ignore")
        for h in self._handlers.get(msg.topic, []):
            try:
                h(msg.topic, payload)
            except Exception as e:
                print("MQTT handler error:", e)

    # ===== public API =====
    def publish(self, topic: str, payload, qos=0, retain=False):
        if self.client is None:
            raise RuntimeError("MQTTService not initialized")
        if not isinstance(payload, (str, bytes)):
            payload = json.dumps(payload, ensure_ascii=False)
        self.client.publish(topic, payload, qos=qos, retain=retain)

    def subscribe(self, topic: str, handler):
        """handler: function(topic:str, payload:str)"""
        self._handlers.setdefault(topic, []).append(handler)
        if self.client and self._connected:
            self.client.subscribe(topic)

# singleton
mqtt = MQTTService()
