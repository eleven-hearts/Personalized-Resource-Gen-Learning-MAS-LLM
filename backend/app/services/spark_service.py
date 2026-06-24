import websocket
import json
import hashlib
import base64
import hmac
from datetime import datetime, timezone
from urllib.parse import urlencode
import threading
from app.core.config import settings


class SparkService:
    """讯飞星火大模型服务封装"""

    def __init__(self):
        self.app_id = settings.SPARK_APP_ID
        self.api_key = settings.SPARK_API_KEY
        self.api_secret = settings.SPARK_API_SECRET
        self.host = "spark-api.xf-yun.com"
        self.path = "/v3.5/chat"

    def is_configured(self) -> bool:
        return all([self.app_id, self.api_key, self.api_secret])

    def _generate_url(self):
        """生成鉴权URL"""
        now = datetime.now(timezone.utc)
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding="utf-8")

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
            encoding="utf-8"
        )

        v = {"authorization": authorization, "date": date, "host": self.host}
        url = f"wss://{self.host}{self.path}?{urlencode(v)}"
        return url

    def chat(self, messages, temperature=0.7, max_tokens=2048):
        """
        同步调用星火大模型对话
        :param messages: 消息列表 [{"role": "user", "content": "..."}]
        :return: 模型回复内容
        """
        if not self.is_configured():
            raise RuntimeError("未配置讯飞星火 API 密钥，请在 backend/.env 中设置 SPARK_APP_ID、SPARK_API_KEY、SPARK_API_SECRET")

        result = {"content": "", "completed": False, "error": ""}

        def on_message(ws, message):
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                result["content"] = f"请求错误: {code}, {data['header']['message']}"
                result["completed"] = True
                ws.close()
                return

            choices = data["payload"]["choices"]
            content = choices["text"][0]["content"]
            result["content"] += content

            if choices["status"] == 2:
                result["completed"] = True
                ws.close()

        def on_error(ws, error):
            result["error"] = f"连接错误: {str(error)}"
            result["completed"] = True

        def on_close(ws, close_status_code, close_msg):
            result["completed"] = True

        def on_open(ws):
            def run():
                data = {
                    "header": {
                        "app_id": self.app_id,
                        "uid": "user001",
                    },
                    "parameter": {
                        "chat": {
                            "domain": "generalv3.5",
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        }
                    },
                    "payload": {
                        "message": {
                            "text": messages,
                        }
                    },
                }
                ws.send(json.dumps(data))

            threading.Thread(target=run).start()

        ws = websocket.WebSocketApp(
            self._generate_url(),
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open,
        )

        ws.run_forever()
        if result["error"]:
            raise RuntimeError(result["error"])
        return result["content"]

    async def chat_stream(self, messages, temperature=0.7, max_tokens=2048):
        """
        流式调用星火大模型（用于SSE/WebSocket）
        TODO: 实现流式输出
        """
        pass


spark_service = SparkService()
