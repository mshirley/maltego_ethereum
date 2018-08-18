from canari.maltego.message import *

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

