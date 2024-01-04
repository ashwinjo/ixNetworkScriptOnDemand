import click
from sod import SessionManager

@click.command()
@click.option('--session_name', help="Give your IxNetwork Session Unique Name")
@click.option('--linux_api_server', default='', help="Give your IxNetwork Session Unique Name")
@click.option('--linux_api_server_username', default='admin', help="Give your IxNetwork Session Unique Name")
@click.option('--linux_api_server_password', default='admin', help="Give your IxNetwork Session Unique Name")
@click.option('--source_chassis_card_ports', default='', help='10.10.10.10;1;5')
@click.option('--dest_chassis_card_ports', default='', help='10.10.10.10;1;6')
@click.option('--linerate', default='', help='50')
@click.option('--packetsize', default='', help='9000')
@click.option('--ixiaconfigfilepath', default='', help='9000')
@click.option('--operation', help='setupSession | startTraffic | stopTraffic | clearCounters| setLineRate | setPacketSize| showPacketLoss')
def parse_args(session_name, linux_api_server, linux_api_server_username, linux_api_server_password,
               source_chassis_card_ports, dest_chassis_card_ports, linerate, packetsize, ixiaconfigfilepath, operation):

    if operation == "setupSession":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name, 
                            username='admin', password=linux_api_server_password)
        sm.create_session_object()
        sm.load_config_in_session(ixiaconfigfilepath)
        sm.map_and_connect_ports(source_chassis_card_ports, dest_chassis_card_ports)
        
    if operation == "startTraffic":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name, 
                            username='admin', password=linux_api_server_password)
        sm.start_traffic()
    
    if operation == "stopTraffic":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name, 
                            username='admin', password=linux_api_server_password)
        sm.stop_traffic()

    if operation == "setLineRate":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name, 
                            username='admin', password=linux_api_server_password)
        sm.set_linerate(linerate)
    
    if operation == "setPacketSize":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name, 
                            username='admin', password=linux_api_server_password)
        sm.set_packetsize(packetsize)
    
    if operation == "clearCounters":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name, 
                            username='admin', password=linux_api_server_password)
        sm.clear_counters()

    if operation == "showPacketLoss":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name,
                             username='admin', password=linux_api_server_password)
        sm.show_statistics()

    if operation == "removeSession":
        sm = SessionManager(linux_api_server=linux_api_server, session_name=session_name,
                             username='admin', password=linux_api_server_password)
        sm.delete_session_object()

if __name__ == '__main__':
    parse_args()


    