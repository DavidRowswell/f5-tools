""" READ F5 SCF FILES AND RETURN SOME INFORMATION..."""
import glob
import os
import re
import sys

from ciscoconfparse import CiscoConfParse


def check_input():
    if len(sys.argv) != 2:
        print 'We need a single (VIP) IP address as input'
        exit(2)


def get_f5_file_path():
    """RETURN THE PATH WHERE THE F5 FILES ARE """
    return os.path.join(os.getcwd(), 'f5_configs', '*.scf')


def get_hostname(parsed_config):
    """RETURN THE HOST NAME OF THE F5"""
    host_line = parsed_config.find_objects(r"hostname")[0].text
    key, f5_hostname = host_line.split()
    return f5_hostname


def find_vip_by_address(filename, hostname, parsed_config, vip_address):
    vip_match_stanzas = parsed_config.find_objects_w_child(parentspec="^ltm virtual ", childspec=vip_address)
    if vip_match_stanzas:
        print("!========================================================")
        print("!FILENAME " + filename)
        print("!========================================================")
        print("!- - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
        print("!HOSTNAME " + hostname)
        print("!- - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
        for vip_match in vip_match_stanzas:
            pool_name = ""
            print vip_match.text
            for child in vip_match.all_children:
                print child.text
            for child in vip_match.children:
                if 'pool' in child.text:
                    if child.text.strip().split(" ")[0] == "pool":
                        pool_name = child.text.strip().split(" ")[1]
            print('}')
            print("!..............................................")
            print("!ASSOCIATED POOL:" + pool_name)
            print("!..............................................")
            regex_pattern = r"^ltm pool " + pool_name + " {"
            pool_match_stanzas = parsed_config.find_objects(regex_pattern)
            if pool_match_stanzas:
                for pool_match in pool_match_stanzas:
                    print pool_match.text
                    for child in pool_match.all_children:
                        print child.text
                    print('}')


def main():
    check_input()
    """FILES PRINTING WHAT WE CAN FIND"""
    # vip = "10.212.64.70"
    vip = sys.argv[1].strip()
    print("!++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("!SEARCHING FOR VIP " + vip)
    print("!++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    for infile in glob.glob(get_f5_file_path()):
        filename = os.path.basename(infile)
        parse = CiscoConfParse(infile)
        hostname = get_hostname(parse)
        vip_address_pattern = re.compile(re.escape(vip))
        find_vip_by_address(filename, hostname, parse, vip_address_pattern)

    print("!========================================================")
    print("!END OF SEARCH")
    print("!========================================================")


if __name__ == '__main__':
    main()
