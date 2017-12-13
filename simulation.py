from network import Router, Host
from link import Link, LinkLayer
import threading
from time import sleep
import sys
from copy import deepcopy

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1000000 #give the network sufficient time to execute transfers

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads at the end

    #create network hosts
    host_1 = Host('H1')
    object_L.append(host_1)
    host_2 = Host('H2')
    object_L.append(host_2)
    host_3 = Host('H3')
    object_L.append(host_3)

    #create routers and routing tables for connected clients (subnets)
    encap_tbl_D = {}    # table used to encapsulate network packets into MPLS frames
    encap_tbl_D['RA'] = {'in_label': ['', ''], 'out_label': [20, 40]}
    frwd_tbl_D = {}     # table used to forward MPLS frames
    frwd_tbl_D['RA'] = {'in_label': ['', ''], 'out_label': [20, 40], 'in_intf': [0, 1], 'out_intf': [1, 0],
                        'dest': ['H2', 'H1', 'H3']}
    decap_tbl_D = {}    # table used to decapsulate network packets from MPLS frames
    router_a = Router(name='RA',
                              intf_capacity_L=[700,700],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_a)

    encap_tbl_D = {}
    encap_tbl_D['RB'] = {'in_label': [20], 'out_label': [30]}
    frwd_tbl_D = {}
    frwd_tbl_D['RB'] = {'in_label': [20], 'out_label': [30], 'in_intf': [0, 1], 'out_int': [1, 0], 'dest': ['H2', 'H1']}
    decap_tbl_D = {}
    router_b = Router(name='RB',
                              intf_capacity_L=[700,700],
                              encap_tbl_D = encap_tbl_D,
                              frwd_tbl_D = frwd_tbl_D,
                              decap_tbl_D = decap_tbl_D,
                              max_queue_size=router_queue_size)
    object_L.append(router_b)

    encap_tbl_D = {}
    encap_tbl_D['RC'] = {'in_label': [40], 'out_label': [50]}
    frwd_tbl_D = {}
    frwd_tbl_D['RC'] = {'in_label': [40], 'out_label': [50], 'in_intf': [0, 1], 'out_int': [1, 0], 'dest': ['H2', 'H1']}
    decap_tbl_D = {}
    router_c = Router(name='RC',
                      intf_capacity_L=[700, 700],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_c)

    encap_tbl_D = {}
    encap_tbl_D['RD'] = {'in_label': [50, 30], 'out_label': ['', '']}
    frwd_tbl_D = {}
    frwd_tbl_D['RD'] = {'in_label': [50, 30], 'out_label': ['', ''], 'in_intf': [0, 1], 'out_int': [1, 0], 'dest': ['H2', 'H1']}
    decap_tbl_D = {}
    router_d = Router(name='RD',
                      intf_capacity_L=[700, 700],
                      encap_tbl_D=encap_tbl_D,
                      frwd_tbl_D=frwd_tbl_D,
                      decap_tbl_D=decap_tbl_D,
                      max_queue_size=router_queue_size)
    object_L.append(router_d)

    #create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    #add all the links - need to reflect the connectivity in cost_D tables above
    link_layer.add_link(Link(host_1, 0, router_a, 0))
    link_layer.add_link(Link(host_2, 0, router_a, 0))
    link_layer.add_link(Link(router_a, 1, router_b, 0))

    link_layer.add_link(Link(router_c, 1, router_d, 0))
    link_layer.add_link(Link(router_b, 1, router_d, 0))
    link_layer.add_link(Link(router_d, 1, host_3, 0))
    link_layer.add_link(Link(router_a, -1, router_c, 0))


    #start all the objects
    thread_L = []
    for obj in object_L:
        thread_L.append(threading.Thread(name=obj.__str__(), target=obj.run))

    for t in thread_L:
        t.start()

    #send some events to demo routing
    host_1.udt_send('H3', 'Wittie is AWESOME_H1')
    #Host 2 sends a packet
    host_2.udt_send('H3', 'Fenil is AWESOME_H2')
    sleep(simulation_time)

    '''
    #create some send events
    for i in range(5):
        priority = i%2
        host_1.udt_send('H2', 'MESSAGE_%d_FROM_H1' % i, priority)
        #host_2.udt_send('H1', 'MESSAGE_%d_FROM_H2' % i, priority)
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    '''


    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")