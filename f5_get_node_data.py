""" READ F5 SCF FILES AND RETURN SOME INFORMATION"""
import glob
import os

from ciscoconfparse import CiscoConfParse


def get_headers():
    """RETURN THE HEADERS FOR THE REST OF THE INFORMATION WE ARE ABOUT TO PRODUCE"""
    return (
        "F5_SCF_FILE_NAME" + "," +
        "F5_HOSTNAME" + "," +
        "F5_PARTITION_NAME" + "," +
        "F5_NODE_NAME" + "," +
        "F5_NODE_ADDRESS"
    )


def get_f5_file_path():
    """RETURN THE PATH WHERE THE F5 FILES ARE """
    return os.path.join(os.getcwd(), 'f5_configs', '*.*')


def get_hostname(parsed_config):
    """RETURN THE HOST NAME OF THE F5"""
    host_line = parsed_config.find_objects(r"hostname")[0].text
    key, f5_hostname = host_line.split()
    return f5_hostname


def get_node_attributes(parsed_config):
    """RETURN NODE ATTRIBUTES AS LIST
    The stanza is of the format:
        ltm node /Common/10.197.5.71 {
            address 10.197.5.71
        }
    """
    result = []
    for config_obj in parsed_config.find_objects(r"^ltm node"):
        config_obj_words = config_obj.text.split(" ")
        f5_node_text = config_obj_words[2]
        nothing, f5_partition, f5_node_name = f5_node_text.strip().split('/')
        children = config_obj.children
        for sub_children in children:
            if 'address' in sub_children.text:
                f5_node_address = sub_children.text.strip().split(" ")[1]
                result.append((f5_partition, f5_node_name, f5_node_address))
    return result


def main():
    """PRINT HEADERS"""
    print get_headers()
    """LOOP THROUGH ALL FILES PRINTING WHAT WE NEED"""
    for infile in glob.glob(get_f5_file_path()):
        filename = os.path.basename(infile)
        parse = CiscoConfParse(infile)
        hostname = get_hostname(parse)
        my_result = get_node_attributes(parse)
        for partition, node_name, node_address in my_result:
            print(filename + "," + hostname + "," + partition + "," + node_name + "," + node_address)


if __name__ == '__main__':
    main()
