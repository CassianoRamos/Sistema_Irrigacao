
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

class AsyncConn:
    def __init__(self, id: str, channel_name: str) -> None:
        config = PNConfiguration()
        config.subscribe_key = 'sub-c-e71d1d1d-845e-4396-abfb-a556997f18ea'
        config.publish_key = 'pub-c-6e5bc9c9-1871-4287-89e7-37ec83a4d2ec'
        config.user_id = id
        config.enable_subscribe = True
        config.daemon = True

        self.pubnub = PubNub(config)
        self.channel_name = channel_name

        print(f"Configurando conexão com o canal '{self.channel_name}'...")
        #subscription = self.pubnub.channel(self.channel_name).subscription()
        #subscription.subscribe()
        self.pubnub.subscribe().channels(self.channel_name).execute()


    def publish(self, data: dict):
        print("tentando enviar uma mensagem")
        self.pubnub.publish().channel(self.channel_name).message(data).sync()

