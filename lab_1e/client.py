from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING,UINT16,ListFieldType,BUFFER,INT,BOOL
import asyncio
import playground
from playground.network.common import StackingProtocol,StackingProtocolFactory,StackingTransport
from passthrough import *

class RstConnectPkg (PacketType):
    DEFINITION_IDENTIFIER = "Request a connection"
    DEFINITION_VERSION = '1.0'

    FIELDS = [
        ("msg", STRING),
        ("ID",UINT16)
    ]

class RstConfirmed(PacketType):
    DEFINITION_IDENTIFIER = "confirm a conneciton"
    DEFINITION_VERSION = '1.0'
    FIELDS = [
        ("ID",UINT16),
        ("con_msg",STRING)

    ]

class BConPkg(PacketType):
    DEFINITION_IDENTIFIER = "start to build a connection"
    DEFINITION_VERSION = '1.0'
    FIELDS = [
        ("con_nect", STRING),
        ("port",UINT16),
        ("ID", UINT16)
    ]

class QuestionP(PacketType):
    DEFINITION_IDENTIFIER = "Question is .."
    DEFINITION_VERSION = '1.0'
    FIELDS = [
        ("Ques",BUFFER),
        ("ID", UINT16)
    ]

class AnswerP(PacketType):
    DEFINITION_IDENTIFIER = "Answer is .."
    DEFINITION_VERSION = '1.0'
    FIELDS = [
        ("answer",BUFFER),

        ("time",INT),
        ("ID",UINT16)
    ]

class CheckP(PacketType):
    DEFINITION_IDENTIFIER = "check the answer"
    DEFINITION_VERSION = '1.0'
    FIELDS = [
        ("result",STRING),
        ("ID", UINT16)
    ]

class C_BConPkg():

    def __init__(self,con_nect,ID,port):
        self.ID=ID
        self.port=port
        self.con_nect= con_nect
    def create(self):
        pac=BConPkg()
        pac.con_nect = self.con_nect
        pac.port = self.port
        pac.ID = self.ID
        return pac

class C_AnswerP():

    def __init__(self,answer,time,ID):
        self.answer= answer
        self.time= time
        self.ID= ID

    def create(self):
        pac=AnswerP()
        pac.answer=self.answer
        pac.time= self.time
        pac.ID= self.ID
        return pac


class Protocol_client(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.state=0

        #self.loop=loop


    def connection_made(self, transport):
        self.transport = transport
        self._deserializer = PacketType.Deserializer()

       # self.transport.write(pkg1.__serialize__())


    def data_received(self, data):
        self._deserializer = PacketType.Deserializer()
        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():

            if isinstance(pkt, RstConfirmed):
                if self.state==0:

                    self.state+=1

                    bd1=C_BConPkg("conneciton made",100,9999)
                    bdpkt=bd1.create()

                    self.transport.write(bdpkt.__serialize__())


            elif isinstance(pkt, QuestionP):
                if self.state==1:
                    print(pkt.Ques)
                    self.state+=1
                    bd1=C_AnswerP(b"I am from China",2017,pkt.ID)
                    bdpkt= bd1.create()
                    self.transport.write(bdpkt.__serialize__())
                else:
                    print("Connection Error!")
            elif isinstance(pkt,CheckP):
                if self.state==2:
                    print(pkt.result)



    def send_packet(self, packet):
            print("send first packet")
            self.transport.write(packet.__serialize__())

    def connection_lost(self, exc):
            print("404! connection lost")
            self.loop.Stop()
if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    #x=loop.create_connection(lambda :Protocol_client(),host='127.0.0.1',port=8888)

    #x = playground.getConnector().create_playground_connection(lambda: Protocol_client(), '1888.1.1.1', 38099)
    x=playground.getConnector('passTo').create_playground_connection(lambda: Protocol_client(), '1888.1.1.1', 38099)
    pkg1 = RstConnectPkg()
    pkg1.msg = "let's build a connection"
    pkg1.ID = 100


    trans,pro=loop.run_until_complete(x)
    pro.send_packet(pkg1)
    loop.run_forever()
    loop.close()