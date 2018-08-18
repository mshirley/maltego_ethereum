from canari.maltego.entities import Person, Phrase, Entity, StringEntityField
from canari.maltego.message import LinkDirection
from canari.maltego.transform import Transform
from canari.framework import EnableDebugWindow
import urllib3
import json
import time
import requests
#from ethjsonrpc import EthJsonRpc

http = urllib3.PoolManager()
#c = EthJsonRpc('127.0.0.1', 8545)

__author__ = 'mshirley'
__copyright__ = 'Copyright 2018, ethereum Project'
__credits__ = []

__license__ = 'GPLv3'
__version__ = '0.1'
__maintainer__ = 'mshirley'
__email__ = 'mshirley@gmail.com'
__status__ = 'Development'



class ETHAddress(Entity):
    _category_ = 'Cryptocurrency'
    _namespace_ = 'maltego'

    properties_ethereumaddress = StringEntityField('properties.ethereumaddress', display_name='Ethereum Address', is_value=True)

class ETHTransaction(Entity):
    _category_ = 'Cryptocurrency'
    _namespace_ = 'maltego'

    properties_ethereumtransaction = StringEntityField('properties.ethereumtransaction', display_name='Ethereum Transaction', is_value=True)
    
class ETHTransactionCall(Entity):
    _category_ = ' Cryptocurrency'
    _namespace_ = 'maltego'

    properties_ethereumtransactioncall = StringEntityField('properties.ethereumtransactioncall', display_name='Ethereum Transaction Call', is_value=True)

class ETHBlock(Entity):
    _category_ = ' Cryptocurrency'
    _namespace_ = 'maltego'

    properties_ethereumblock = StringEntityField('properties.ethereumblock', display_name='Ethereum Block', is_value=True)

@EnableDebugWindow
class TransactionsFromAddress(Transform):

    input_type = ETHAddress 

    def do_transform(self, request, response, config):
        ethaddress = request.entity
        json_response = json.loads(http.request('GET','api.blockcypher.com/v1/eth/main/addrs/{}'.format(ethaddress.properties_ethereumaddress)).data)
        if 'txrefs' not in json_response:
            time.sleep(5)
            json_response = json.loads(http.request('GET','api.blockcypher.com/v1/eth/main/addrs/{}'.format(ethaddress.properties_ethereumaddress)).data)
        for txrefs in json_response['txrefs']:
            tx = ETHTransaction('0x' + txrefs['tx_hash'])
            if txrefs['tx_input_n'] == -1:
                tx.link_direction = LinkDirection.OutputToInput
                #tx.link_label = 'received'
            if txrefs['tx_output_n'] == -1:
                tx.link_direction = LinkDirection.InputToOutput
                #tx.link_label = 'sent'
            response += tx
            
        return response
    

    def on_terminate(self):
        """
        This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms.
        """
        pass

@EnableDebugWindow    
class AddressFromTransaction(Transform):

    input_type = ETHTransaction

    def do_transform(self, request, response, config):
        ethaddress = request.entity
        json_response = json.loads(http.request('GET','http://api.blockcypher.com/v1/eth/main/txs/{}'.format(ethaddress.properties_ethereumtransaction)).data)
        if 'inputs' not in json_response or 'outputs' not in json_response:
            time.sleep(5)
            json_response = json.loads(http.request('GET','http://api.blockcypher.com/v1/eth/main/txs/{}'.format(ethaddress.properties_ethereumtransaction)).data)
        for i in json_response['inputs']:
            for address in i['addresses']:
                addr = ETHAddress('0x' +address)
                addr.link_direction = LinkDirection.OutputToInput
                #addr.link_label = 'received'
                response += addr
        for o in json_response['outputs']:
            for address in o['addresses']:
                addr = ETHAddress('0x' +address)
                addr.link_direction = LinkDirection.InputToOutput
                #addr.link_label = 'sent'
                response += addr
        return response
    

    def on_terminate(self):
        """
        This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms.
        """
        pass


    
@EnableDebugWindow    
class GethAddressFromTransaction(Transform):

    input_type = ETHTransaction

    def do_transform(self, request, response, config):
        # create persistent HTTP connection
        session = requests.Session()
        # as defined in https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version
        method = 'eth_getTransactionByHash'
        ethaddress = request.entity
        params = [ethaddress.properties_ethereumtransaction]
        payload= {"jsonrpc":"2.0",
           "method":method,
           "params":params,
           "id":1}
        headers = {'Content-type': 'application/json'}
        
        tx = session.post('http://localhost:8545', json=payload, headers=headers).json()
        if 'result' in tx and not tx['result'] == None:
            from_addr = ETHAddress(tx['result']['from'])
            to_addr = ETHAddress(tx['result']['to'])
            #from_addr.link_label = 'sent'
            #to_addr.link_label = 'received'
            response += from_addr
            response += to_addr
        return response
    

    def on_terminate(self):
        """
        This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms.
        """
        pass

@EnableDebugWindow    
class ParityTraceTransaction(Transform):

    input_type = ETHTransaction

    def do_transform(self, request, response, config):
        # create persistent HTTP connection
        session = requests.Session()
        # as defined in https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version
        method = 'trace_transaction'
        ethaddress = request.entity
        params = [ethaddress.properties_ethereumtransaction]
        payload= {"jsonrpc":"2.0",
           "method":method,
           "params":params,
           "id":1}
        headers = {'Content-type': 'application/json'}
        
        tx = session.post('http://localhost:8545', json=payload, headers=headers).json()
        if 'result' in tx and not tx['result'] == None:
            for r in tx['result']:
                if 'action' in r and 'callType' in r['action']:
                    call_type = ETHTransactionCall(r['action']['callType'])
                    block = Phrase(r['blockNumber'])
                    response += call_type
                    response += block
        return response
    

    def on_terminate(self):
        """
        This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms.
        """
        pass
@EnableDebugWindow    

class ParityTraceBlock(Transform):

    input_type = Phrase

    def do_transform(self, request, response, config):
        # create persistent HTTP connection
        session = requests.Session()
        # as defined in https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version
        method = 'trace_block'
        ethblock = request.entity
        block_num = hex(int(ethblock.text))
        params = [block_num]
        payload= {"jsonrpc":"2.0",
           "method":method,
           "params":params,
           "id":1}
        headers = {'Content-type': 'application/json'}
        
        block = session.post('http://localhost:8545', json=payload, headers=headers).json()
        if 'result' in block and not block['result'] == None:
            for r in block['result']:
                if 'action' in r and 'callType' in r['action']:
                    call_type = ETHTransactionCall(r['action']['callType'])
                    response += call_type
                    from_addr = ETHAddress(r['action']['from'])
                    to_addr = ETHAddress(r['action']['to'])
                    from_addr.link_label = 'from'
                    to_addr.link_label = 'to'
                    response += from_addr
                    response += to_addr
        return response
    

    def on_terminate(self):
        """
        This method gets called when transform execution is prematurely terminated. It is only applicable for local
        transforms.
        """
        pass