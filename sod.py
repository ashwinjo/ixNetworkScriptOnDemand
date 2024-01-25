from ixnetwork_restpy import SessionAssistant, Files, BatchUpdate
from tabulate import tabulate

class TrafficGenerator():
    def __init__(self, ixNetwork=None):
        self.ixNetwork = ixNetwork

    def start_traffic(self):
        traffic_items = self.ixNetwork.Traffic.TrafficItem.find()
        self.ixNetwork.Traffic.Apply()
        self.ixNetwork.Traffic.StartStatelessTrafficBlocking()

    def stop_traffic(self):
        self.ixNetwork.Traffic.StopStatelessTrafficBlocking()

    def clear_counters(self):
        self.ixNetwork.ClearPortsAndTrafficStats()
    
    def set_linerate(self, linerate=None):
        traffic_items = self.ixNetwork.Traffic.TrafficItem.find()
        # we are using batch update to update some of traffic parameters and parameters of its sub child
        with BatchUpdate(self.ixNetwork):
            for idx, traffic_item in enumerate(traffic_items):
                flgroups = traffic_item.HighLevelStream.find()
                flgroups.FrameRate.find().Rate = linerate
        self.ixNetwork.Traffic.TrafficItem.find().Generate()
                
    def set_packetsize(self, packetsize=None):
        traffic_items = self.ixNetwork.Traffic.TrafficItem.find()
        # we are using batch update to update some of traffic parameters and parameters of its sub child
        with BatchUpdate(self.ixNetwork):
            for idx, traffic_item in enumerate(traffic_items):
                flgroups = traffic_item.HighLevelStream.find()
                flgroups.FrameSize.find().FixedSize = str(packetsize)
                flgroups.FrameSize.find().Type = "fixed"
        self.ixNetwork.Traffic.TrafficItem.find().Generate()

        
class SessionManager():
    def __init__(self, linux_api_server=None, session_name=None, 
                 username=None, password=None) -> None:
        self.linux_api_server = linux_api_server
        self.session_name = session_name
        self.username = username
        self.password = password
    
    def create_session_object(self):
        SessionAssistant(IpAddress=self.linux_api_server, RestPort=None, UserName=self.username, 
                                   Password=self.password, 
                                   SessionName=self.session_name, SessionId=None, 
                                   ApiKey=None,
                                   ClearConfig=False, 
                                   LogLevel='info', 
                                   LogFilename='restpy.log')
        
    def delete_session_object(self):
        session = self.get_session_object()
        session.Session.remove()


    def get_session_object(self):
        return SessionAssistant(IpAddress=self.linux_api_server, RestPort=None, UserName=self.username, 
                                Password=self.password, 
                                SessionName=self.session_name, SessionId=None, 
                                ApiKey=None,
                                ClearConfig=False, 
                                LogLevel='info', 
                                LogFilename='restpy.log')

    def load_config_in_session(self, ixiaconfigfilepath):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        ixNetwork.info('Loading config file: {0}'.format(ixiaconfigfilepath))
        ixNetwork.LoadConfig(Files(ixiaconfigfilepath, local_file=True))


    def map_and_connect_ports(self, source_chassis_card_ports, dest_chassis_card_ports):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        portList = []
        # source_chassis_card_ports = ['10.10.10.10;1;5', '10.10.10.10;1;6']
        # dest_chassis_card_ports = ['10.10.10.10;2;5', '10.10.10.10;2;6']

        # Assign ports. Map physical ports to the configured vports.
        for source_chassis_card_port in source_chassis_card_ports.split(","):
            chassis_a, card_a, port_a = source_chassis_card_port.strip().split(";")
            portList.append([chassis_a, card_a, port_a])
        
        for dest_chassis_card_port in dest_chassis_card_ports.split(","):
            chassis_b, card_b, port_b = dest_chassis_card_port.strip().split(";")
            portList.append([chassis_b, card_b, port_b])

        print(portList)

        portMap = session.PortMapAssistant()
        for index,port in enumerate(portList):
            # For the port name, get the loaded configuration's port name
            portName = ixNetwork.Vport.find()[index].Name
            portMap.Map(IpAddress=port[0], CardId=port[1], PortId=port[2], Name=portName)
            
        portMap.Connect(True)
    
    def verify_control_plane_up(self):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        ixNetwork.StartAllProtocols(Arg1='sync')
        ixNetwork.info('Verify protocol sessions\n')
        protocolSummary = session.StatViewAssistant('Protocols Summary')
        protocolSummary.CheckCondition('Sessions Not Started', protocolSummary.EQUAL, 0)
        protocolSummary.CheckCondition('Sessions Down', protocolSummary.EQUAL, 0)
        ixNetwork.info(protocolSummary)

    def show_statistics(self):
        session = self.get_session_object() 
        flowStatistics = session.StatViewAssistant('Flow Statistics')

        headers = ['Tx Port', 'Rx Port', 'Loss %', 'TxFrames', 'Rx Frames', 'Rx Expected Frames']
        data = []
        for rowNumber,flowStat in enumerate(flowStatistics.Rows):
            try:
                data.append([flowStat['Tx Port'], flowStat['Rx Port'], flowStat['Loss %'], flowStat['Tx Frames'], flowStat['Rx Frames'], flowStat['Rx Expected Frames']])
            except IndexError:
                data.append([flowStat['Tx Port'], flowStat['Rx Port'], flowStat['Loss %'], flowStat['Tx Frames'], flowStat['Rx Frames'], "NA"])
        print(tabulate(data, headers=headers, tablefmt='grid'))
                   
    def start_traffic(self):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        tg = TrafficGenerator(ixNetwork=ixNetwork)
        tg.start_traffic()

    def stop_traffic(self):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        tg = TrafficGenerator(ixNetwork=ixNetwork)
        tg.stop_traffic()
    
    def set_linerate(self, linerate):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        tg = TrafficGenerator(ixNetwork=ixNetwork)
        tg.set_linerate(linerate)
    
    def set_packetsize(self, packetsize):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        tg = TrafficGenerator(ixNetwork=ixNetwork)
        tg.set_packetsize(packetsize)

    def clear_counters(self):
        session = self.get_session_object() 
        ixNetwork = session.Ixnetwork
        tg = TrafficGenerator(ixNetwork=ixNetwork)
        tg.clear_counters()

    def get_quick_flow_groups():
        pass
        

