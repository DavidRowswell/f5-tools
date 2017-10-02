""" READ F5 SCF FILES AND RETURN SOME INFORMATION"""
import glob
import os

from ciscoconfparse import CiscoConfParse


def get_headers():
    """RETURN THE HEADERS FOR THE REST OF THE INFORMATION WE ARE ABOUT TO PRODUCE"""
    return (
        "F5_SCF_FILE_NAME" + "," +
        "F5_HOST_NAME" + "," +
        "F5_PARTITION_NAME" + "," +
        "F5_VLAN_NAME"
    )


def get_f5_file_path():
    """RETURN THE PATH WHERE THE F5 FILES ARE """
    return os.path.join(os.getcwd(), 'f5_configs', '*.*')


def get_hostname(parsed_config):
    """RETURN THE HOST NAME OF THE F5"""
    host_line = parsed_config.find_objects(r"hostname")[0].text
    key, f5_hostname = host_line.split()
    return f5_hostname


# noinspection SpellCheckingInspection
def get_vlan_attributes(parsed_config):
    # noinspection SpellCheckingInspection
    """RETURN VLAN AND PARTITION NAME AS LIST
        The stanza is of the format:
            net route-domain /Common/0 {
                id 0
                vlans {
                    /Common/VLAN100
                    /Common/VLAN104
                    ...
                }
            }
        """
    result = []
    for config_obj in parsed_config.find_objects(r"^net route-domain /Common/0"):
        children = config_obj.children
        for sub_children in children:
            if 'vlans {' in sub_children.text:
                vlan_children = sub_children.children
                for vlan_line in vlan_children:
                    nothing, f5_partition, f5_vlan = vlan_line.text.split('/')
                    result.append((f5_partition, f5_vlan))
    return result


def main():
    """PRINT HEADERS"""
    print get_headers()

    """LOOP THROUGH ALL FILES PRINTING WHAT WE CAN FIND"""
    for infile in glob.glob(get_f5_file_path()):
        filename = os.path.basename(infile)
        parse = CiscoConfParse(infile)
        hostname = get_hostname(parse)
        my_result = get_vlan_attributes(parse)
        for partition, vlan in my_result:
            print(filename + "," + hostname + "," + partition + "," + vlan)


if __name__ == '__main__':
    main()
