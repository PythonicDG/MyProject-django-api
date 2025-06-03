from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("orders", self.channel_name)
        print(self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("orders", self.channel_name)
        print(self.channel_name)

    async def receive(self, text_data):
        txt_data_json = json.loads(text_data)
        message = txt_data_json['message']

        print(f"Received message: {message}")

        

    async def send_order_notification(self, event):
        await self.send(text_data=json.dumps(event["data"]))


