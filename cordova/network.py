from jarabe.model import network

import logging

def get_network_type():
    network_connection_obj=network.get_connections()
    network_connections=network_connection_obj.get_list()
    logging.error("network connections : %s",network_connections)
    return 'wifi'
