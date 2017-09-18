import asyncio
import playground
from playground.network.common import StackingProtocol,StackingProtocolFactory,StackingTransport

#pass through server
class passThrough1(StackingProtocol):
    def __init__(self):
        super().__init__
        self.transport=None

    def connection_made(self,transport):
        print("Server: start a connection")
        self.transport=transport
        htransport= StackingTransport(self.transport)
        self.higherProtocol().connection_made(htransport)



    def data_received(self,data):
        print("Server: transport ")
        self.higherProtocol().data_received(data)

    def connection_lost(self,exc=None):
        print("Server: connection lost")
        self.higherProtocol().connection_lost()
        self.transport=None

#pass through client
class passThrough2(StackingProtocol):
    def __init__(self):
        super().__init__
        self.transport=None

    def connection_made(self, transport):
        print("Client: start a connection")
        self.transport=transport
        htransport= StackingTransport(self.transport)
        self.higherProtocol().connection_made(htransport)
    def data_received(self, data):
        print("Client :data received")
        self.higherProtocol().data_received(data)
        if self.higherProtocol().state==3:
            self.transport.lost()

    def connection_lost(self, exc=None):
        print("Client : connection lost")
        self.higherProtocol().connection_lost()
        self.transport=None

f = StackingProtocolFactory(lambda: passThrough1(), lambda: passThrough2())
ptConnector= playground.Connector(protocolStack=f)
playground.setConnector("passTo",ptConnector)
