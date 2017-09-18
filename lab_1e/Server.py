import asyncio
import playground
import sys
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import STRING,UINT16,ListFieldType,BUFFER,INT,BOOL
from playground.asyncio_lib.testing import TestLoopEx
from passthrough import *
from playground.network.common import StackingProtocol,StackingProtocolFactory,StackingTransport

###
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

class Protocol_server(asyncio.Protocol):
    def __init__(self):
        self.transport = None


    def connection_made(self, transport):
        print("server connected to client")
        self.transport = transport
        self._deserializer= PacketType.Deserializer()

    def check_id(self, ID):
        arr ={100,200,300,400,500,607,893}
        if ID in arr :

            return True
        else:
            return False



    def data_received(self, data):

        self._deserializer.update(data)
        for pkt in self._deserializer.nextPackets():
           if  isinstance( pkt,RstConnectPkg):
# check whether user is in the list
                cc= self.check_id(pkt.ID)
                if   cc:
                    print(pkt.msg)
                    back_packet = RstConfirmed()
                    back_packet.con_msg = "I agreed"
                    back_packet.ID = pkt.ID
                    self.transport.write(back_packet.__serialize__())
                else :
                        print("illegal Visitor! contact the manager!")

           elif isinstance(pkt,BConPkg):

                print(pkt.con_nect)

                if self.check_id(pkt.ID):
                     back_packet = QuestionP()
                     back_packet.Ques = b'where are you from?'
                     back_packet.ID = pkt.ID

                     self.transport.write(back_packet.__serialize__())

           elif isinstance(pkt,AnswerP):

              #print(pkt.answer)

              if pkt.answer == b"I am from China":
                    print(pkt.answer)
                    back_packet = CheckP()
                    back_packet.result = "true"
                    back_packet.ID = pkt.ID
                    self.transport.write(back_packet.__serialize__())
              else:
                    back_packet= CheckP()
                    back_packet.result = "false"
                    back_packet.ID = pkt.ID
                    self.transport.write(back_packet.__serialize__())

    def connection_lost(self, exc):
        print("404! connection lost")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.set_debug(1)
    #y= playground.getConnector().create_playground_server(lambda:Protocol_server(),38099)
    #y=loop.create_server(lambda :Protocol_server(),port=8888)
    y= playground.getConnector('passTo').create_playground_server(lambda: Protocol_server(),38099)
#
    server = loop.run_until_complete(y)


    loop.run_forever()
    server.close()
    loop.close()