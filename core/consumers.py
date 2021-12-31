import asyncio, json
from channels.generic.websocket import AsyncWebsocketConsumer

class CodeRunConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "user_" + str(self.scope['url_route']['kwargs']['uid'])
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def sendStatus(self, event):
        lst = event['text'].split('/')
        state = lst[0]
        currTc = lst[1]
        totTc = lst[2]
        await self.send(json.dumps({"text" : state + "-" + currTc, "is_testcase" : True}))

    async def sendResult(self, event):
        await self.send(json.dumps({"text" : event['text'], "is_testcase" : False}))
        await self.close()