import json
from channels.generic.websocket import AsyncWebsocketConsumer

NEWS_GROUP = "news_updates"


class NewsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(NEWS_GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(NEWS_GROUP, self.channel_name)

    # 收到 group_send 的 news.update 事件時觸發
    async def news_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "news_update",
            "count": event["count"],
        }))
