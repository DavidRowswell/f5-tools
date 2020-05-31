""" GIVEN AN INPUT FILE OF VIP ADDRESSES, OUTPUT A FILE OF ....,<vip_ip_address>, <node_ip_address> """
import glob
import os
import re
import sys

from ciscoconfparse import CiscoConfParse


def check_input():
    if len(sys.argv) != 2:
        print 'I need a file of VIP IP Addresses, one line per VIP'
        exit(2)


def open_f5_vip_address_file():
    """RETURN THE PATH WHERE THE F5 FILES ARE """
    # f = open(sys.argv[1].strip())


def get_f5_file_path():
    """RETURN THE PATH WHERE THE F5 FILES ARE """
    return os.path.join(os.getcwd(), 'f5_configs', '*.*')


def get_hostname(parsed_config):
    """RETURN THE HOST NAME OF THE F5"""
    host_line = parsed_config.find_objects(r"hostname")[0].text
    key, f5_hostname = host_line.split()
    return f5_hostname


def find_vip_by_address(filename, hostname, parsed_config, vip_address, vip_address_pattern):
    vip_match_stanzas = parsed_config.find_objects_w_child(parentspec="^ltm virtual ", childspec=vip_address_pattern)
    if vip_match_stanzas:
        for vip_match in vip_match_stanzas:
            pool_name = ""
            for child in vip_match.children:
                if (
                    'pool' in child.text
                    and child.text.strip().split(" ")[0] == "pool"
                ):
                    pool_name = child.text.strip().split(" ")[1]
            regex_pattern = r"^ltm pool " + pool_name + " {"
            pool_match_stanzas = parsed_config.find_objects(regex_pattern)
            if pool_match_stanzas:
                for pool_match in pool_match_stanzas:
                    for child in pool_match.all_children:
                        if (
                            'address' in child.text
                            and child.text.strip().split(" ")[0] == "address"
                        ):
                            node_ip_address = child.text.strip().split(" ")[1]
                            print(filename + "," + hostname + "," + vip_match.text.split(" ")[
                                2] + "," + vip_address + "," + node_ip_address)


def main():
    """FILES PRINTING WHAT WE CAN FIND"""
    vip_address_file = open(sys.argv[1].strip())
    for vip_address in vip_address_file:
        vip_address = vip_address.strip()
        for infile in glob.glob(get_f5_file_path()):
            filename = os.path.basename(infile)
            parse = CiscoConfParse(infile)
            hostname = get_hostname(parse)
            vip_address_pattern = re.compile(re.escape(vip_address))
            find_vip_by_address(filename, hostname, parse, vip_address, vip_address_pattern)


if __name__ == '__main__':
    main()
