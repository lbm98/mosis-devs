from pypdevs.DEVS import CoupledDEVS

from generator import Generator
from anchor_point import AnchorPoint
from sea import Sea
from dock import Dock
from lock import Lock
from uni_canal import UniCanal
from canal import Canal
from waterway import Waterway
from uni_waterway import UniWaterway
from confluence import Confluence
from control_tower import ControlTower


class PortNetwork(CoupledDEVS):
    """
    This is a CoupledDEVS of the full port network
    """
    def __init__(self, name: str):
        CoupledDEVS.__init__(self, name)

        # CREATE ALL SUBMODELS
        # The vessel generator
        self.generator = self.addSubModel(Generator('Generator', 10))

        # The anchor point K
        self.anchor_point = self.addSubModel(AnchorPoint('K'))

        # The sea S (which is a collector)
        self.sea_collector = self.addSubModel(Sea('S'))

        # The Docks 1-8
        self.dock_1 = self.addSubModel(Dock('1'))
        self.dock_2 = self.addSubModel(Dock('2'))
        self.dock_3 = self.addSubModel(Dock('3'))
        self.dock_4 = self.addSubModel(Dock('4'))
        self.dock_5 = self.addSubModel(Dock('5'))
        self.dock_6 = self.addSubModel(Dock('6'))
        self.dock_7 = self.addSubModel(Dock('7'))
        self.dock_8 = self.addSubModel(Dock('8'))

        # The Locks A, B and C
        self.lock_a = self.addSubModel(Lock('A', 20*60, 60*60, 7*60, 62500))
        self.lock_b = self.addSubModel(Lock('B', 12*60, 45*60, 5*60, 34000))
        self.lock_c = self.addSubModel(Lock('C', 8*60, 30*60, 5*60, 25650))

        # Uni waterways (K to first node, first node to S)
        self.uniwaterway1 = self.addSubModel(UniWaterway('K_to_node', 47.52))
        self.uniwaterway2 = self.addSubModel(UniWaterway('node_to_S', 30.85))

        # The 4 (two directional) Waterways
        self.waterway1 = self.addSubModel(Waterway('node_to_CP', 68.54))
        self.waterway2 = self.addSubModel(Waterway('CP_to_A', 2.10))
        self.waterway3 = self.addSubModel(Waterway('CP_to_node', 4.70))
        self.waterway4 = self.addSubModel(Waterway('node_to_C', 5.16))

        # The canals
        self.canal1 = self.addSubModel(Canal('A_to_node', 0.8))
        self.canal2 = self.addSubModel(Canal('node_to_1', 1.89))
        self.canal3 = self.addSubModel(Canal('node_to_node_1', 2.39))
        self.canal4 = self.addSubModel(Canal('node_to_2', 1.13))
        self.canal5 = self.addSubModel(Canal('node_to_node_2', 5.70))
        self.canal6 = self.addSubModel(Canal('node_to_3', 1.86))
        self.canal7 = self.addSubModel(Canal('node_to_4', 1.30))
        self.canal8 = self.addSubModel(Canal('node_to_5', 1.68))
        self.canal9 = self.addSubModel(Canal('C_to_node', 1.08))
        self.canal10 = self.addSubModel(Canal('node_to_B', 3.14))
        self.canal11 = self.addSubModel(Canal('B_to_node', 0.89))
        self.canal12 = self.addSubModel(Canal('node_to_node_3', 1.24))
        self.canal13 = self.addSubModel(Canal('node_to_6', 1.37))
        self.canal14 = self.addSubModel(Canal('node_to_7', 1.07))
        self.canal15 = self.addSubModel(Canal('node_to_8', 2.40))

        # The confluences, dock 9 denotes the SEA dock when vessels leave the port
        self.confluence1 = self.addSubModel(Confluence('CP', {
            "sea_port": ["9"],
            "A_port": ["1", "2"],
            "B_C_port": ["3", "4", "5", "6", "7", "8"],
        }))

        self.confluence2 = self.addSubModel(Confluence('CP_B_C', {
            "sea_port": ["9"],
            "C_port": ["3", "4", "5"],
            "B_port": ["6", "7", "8"],
        }))

        self.confluence3 = self.addSubModel(Confluence('A_1_2', {
            "sea_port": ["9"],
            "1_port": ["1"],
            "2_port": ["2"],
        }))

        self.confluence4 = self.addSubModel(Confluence('A_2_C', {
            "sea_port": ["9"],
            "2_port": ["2"],
            "3_4_5_port": ["3", "4", "5"],
        }))

        self.confluence5 = self.addSubModel(Confluence('C_3_4_5', {
            "sea_port": ["9"],
            "3_port": ["3"],
            "4_port": ["4"],
            "5_port": ["5"],
            "1_2_port": ["1", "2"]
        }))

        self.confluence6 = self.addSubModel(Confluence('B_6_7_8', {
            "sea_port": ["9"],
            "8_port": ["8"],
            "6_7_port": ["6", "7"],
        }))

        self.confluence7 = self.addSubModel(Confluence('B_6_7', {
            "sea_port": ["9"],
            "6_port": ["6"],
            "7_port": ["7"],
        }))

        # The control tower
        self.control_tower = self.addSubModel(ControlTower("Control_tower", {
            "1": 50,
            "2": 50,
            "3": 50,
            "4": 50,
            "5": 50,
            "6": 50,
            "7": 50,
            "8": 50
        }))

        # CONNECT PORTS
        # Connect generator, anchorpoint, sea, uniwaterway1, uniwaterway2, waterway 1 and CP confluence1
        self.connectPorts(self.generator.out, self.anchor_point.in_vessel)
        self.connectPorts(self.anchor_point.out_vessel, self.uniwaterway1.in_vessel)
        self.connectPorts(self.uniwaterway1.out_vessel, self.waterway1.in1)
        self.connectPorts(self.waterway1.out2, self.uniwaterway2.in_vessel)
        self.connectPorts(self.uniwaterway2.out_vessel, self.sea_collector.in_vessel)
        self.connectPorts(self.waterway1.out1, self.confluence1.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence1.out_vessel_ports['sea_port'], self.waterway1.in2)

        # Connect waterway2, CP confluence1 en lock a
        self.connectPorts(self.confluence1.out_vessel_ports['A_port'], self.waterway2.in1)
        self.connectPorts(self.waterway2.out2, self.confluence1.in_vessel_ports['A_port'])
        self.connectPorts(self.waterway2.out1, self.lock_a.in_high)
        self.connectPorts(self.lock_a.out_high, self.waterway2.in2)

        # connect waterway 3, CP confluence1, next confluence2
        self.connectPorts(self.confluence1.out_vessel_ports['B_C_port'], self.waterway3.in1)
        self.connectPorts(self.waterway3.out2, self.confluence1.in_vessel_ports['B_C_port'])
        self.connectPorts(self.waterway3.out1, self.confluence2.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence2.out_vessel_ports['sea_port'], self.waterway3.in2)

        # connect waterway 4, confluence2 and lock c
        self.connectPorts(self.confluence2.out_vessel_ports['C_port'], self.waterway4.in1)
        self.connectPorts(self.waterway4.out2, self.confluence2.in_vessel_ports['C_port'])
        self.connectPorts(self.waterway4.out1, self.lock_c.in_high)
        self.connectPorts(self.lock_c.out_high, self.waterway4.in2)

        # connect lock a, canal1, confluence3
        self.connectPorts(self.lock_a.out_low, self.canal1.in1)
        self.connectPorts(self.canal1.out2, self.lock_a.in_low)
        self.connectPorts(self.canal1.out1, self.confluence3.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence3.out_vessel_ports['sea_port'], self.canal1.in2)

        # connect confluence3, canal2, dock1
        self.connectPorts(self.confluence3.out_vessel_ports['1_port'], self.canal2.in1)
        self.connectPorts(self.canal2.out2, self.confluence3.in_vessel_ports['1_port'])
        self.connectPorts(self.canal2.out1, self.dock_1.in_vessel)
        self.connectPorts(self.dock_1.out_vessel, self.canal2.in2)

        # connect confluence3, canal3, confluence4
        self.connectPorts(self.confluence3.out_vessel_ports['2_port'], self.canal3.in1)
        self.connectPorts(self.canal3.out2, self.confluence3.in_vessel_ports['2_port'])
        self.connectPorts(self.canal3.out1, self.confluence4.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence4.out_vessel_ports['sea_port'], self.canal3.in2)

        # connect confluence4, canal4, dock2
        self.connectPorts(self.confluence4.out_vessel_ports['2_port'], self.canal4.in1)
        self.connectPorts(self.canal4.out2, self.confluence4.in_vessel_ports['2_port'])
        self.connectPorts(self.canal4.out1, self.dock_2.in_vessel)
        self.connectPorts(self.dock_2.out_vessel, self.canal4.in2)

        # connect confluence4, canal5, confluence5
        self.connectPorts(self.confluence4.out_vessel_ports['3_4_5_port'], self.canal5.in1)
        self.connectPorts(self.canal5.out2, self.confluence4.in_vessel_ports['3_4_5_port'])
        self.connectPorts(self.canal5.out1, self.confluence5.in_vessel_ports['1_2_port'])
        self.connectPorts(self.confluence5.out_vessel_ports['1_2_port'], self.canal5.in2)

        # connect confluence5, canal6, dock3
        self.connectPorts(self.confluence5.out_vessel_ports['3_port'], self.canal6.in1)
        self.connectPorts(self.canal6.out2, self.confluence5.in_vessel_ports['3_port'])
        self.connectPorts(self.canal6.out1, self.dock_3.in_vessel)
        self.connectPorts(self.dock_3.out_vessel, self.canal6.in2)

        # connect confluence5, canal7, dock4
        self.connectPorts(self.confluence5.out_vessel_ports['4_port'], self.canal7.in1)
        self.connectPorts(self.canal7.out2, self.confluence5.in_vessel_ports['4_port'])
        self.connectPorts(self.canal7.out1, self.dock_4.in_vessel)
        self.connectPorts(self.dock_4.out_vessel, self.canal7.in2)

        # connect confluence5, canal8, dock5
        self.connectPorts(self.confluence5.out_vessel_ports['5_port'], self.canal8.in1)
        self.connectPorts(self.canal8.out2, self.confluence5.in_vessel_ports['5_port'])
        self.connectPorts(self.canal8.out1, self.dock_5.in_vessel)
        self.connectPorts(self.dock_5.out_vessel, self.canal8.in2)

        # connect lock c, canal9, confluence5
        self.connectPorts(self.lock_c.out_low, self.canal9.in1)
        self.connectPorts(self.canal9.out2, self.lock_c.in_low)
        self.connectPorts(self.canal9.out1, self.confluence5.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence5.out_vessel_ports['sea_port'], self.canal9.in2)

        # connect confluence2, canal10, lock b
        self.connectPorts(self.confluence2.out_vessel_ports['B_port'], self.canal10.in1)
        self.connectPorts(self.canal10.out2, self.confluence2.in_vessel_ports['B_port'])
        self.connectPorts(self.canal10.out1, self.lock_b.in_high)
        self.connectPorts(self.lock_b.out_high, self.canal10.in2)

        # connect lock b, canal11, confluence6
        self.connectPorts(self.lock_b.out_low, self.canal11.in1)
        self.connectPorts(self.canal11.out2, self.lock_b.in_low)
        self.connectPorts(self.canal11.out1, self.confluence6.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence6.out_vessel_ports['sea_port'], self.canal11.in2)

        # connect confluence6, canal12, confluence7
        self.connectPorts(self.confluence6.out_vessel_ports['6_7_port'], self.canal12.in1)
        self.connectPorts(self.canal12.out2, self.confluence6.in_vessel_ports['6_7_port'])
        self.connectPorts(self.canal12.out1, self.confluence7.in_vessel_ports['sea_port'])
        self.connectPorts(self.confluence7.out_vessel_ports['sea_port'], self.canal12.in2)

        # connect confluence7, canal13, dock6
        self.connectPorts(self.confluence7.out_vessel_ports['6_port'], self.canal13.in1)
        self.connectPorts(self.canal13.out2, self.confluence7.in_vessel_ports['6_port'])
        self.connectPorts(self.canal13.out1, self.dock_6.in_vessel)
        self.connectPorts(self.dock_6.out_vessel, self.canal13.in2)

        # connect confluence7, canal14, dock7
        self.connectPorts(self.confluence7.out_vessel_ports['7_port'], self.canal14.in1)
        self.connectPorts(self.canal14.out2, self.confluence7.in_vessel_ports['7_port'])
        self.connectPorts(self.canal14.out1, self.dock_7.in_vessel)
        self.connectPorts(self.dock_7.out_vessel, self.canal14.in2)

        # connect confluence6, canal15, dock8
        self.connectPorts(self.confluence6.out_vessel_ports['8_port'], self.canal15.in1)
        self.connectPorts(self.canal15.out2, self.confluence6.in_vessel_ports['8_port'])
        self.connectPorts(self.canal15.out1, self.dock_8.in_vessel)
        self.connectPorts(self.dock_8.out_vessel, self.canal15.in2)

        # connect control tower and anchor point
        self.connectPorts(self.anchor_point.out_port_entry_request, self.control_tower.in_port_entry_request)
        self.connectPorts(self.control_tower.out_port_entry_permission, self.anchor_point.in_port_entry_permission)

        # connect docks and control tower
        self.connectPorts(self.dock_1.out_port_departure_request, self.control_tower.in_port_departure_requests['1'])
        self.connectPorts(self.dock_2.out_port_departure_request, self.control_tower.in_port_departure_requests['2'])
        self.connectPorts(self.dock_3.out_port_departure_request, self.control_tower.in_port_departure_requests['3'])
        self.connectPorts(self.dock_4.out_port_departure_request, self.control_tower.in_port_departure_requests['4'])
        self.connectPorts(self.dock_5.out_port_departure_request, self.control_tower.in_port_departure_requests['5'])
        self.connectPorts(self.dock_6.out_port_departure_request, self.control_tower.in_port_departure_requests['6'])
        self.connectPorts(self.dock_7.out_port_departure_request, self.control_tower.in_port_departure_requests['7'])
        self.connectPorts(self.dock_8.out_port_departure_request, self.control_tower.in_port_departure_requests['8'])


