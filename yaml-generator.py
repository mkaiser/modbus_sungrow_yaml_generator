#!/usr/bin/env python3
from ruamel.yaml import YAML
from collections import OrderedDict
from ruamel.yaml.comments import CommentedMap

def filter_yaml(yaml_data, fParam):

    yaml_data_filtered = yaml_data

    return yaml_data_filtered

def processYaml(input_file, output_file, fParam):
    # Read YAML from input file
    with open(input_file, 'r') as f:
        yaml = YAML()
        yaml_data = yaml.load(f)

    print (type(yaml_data))    
    print("parsed yaml: \n", yaml_data, "\n\n")

    print ("\n\n fParam=", fParam,  "\n\n")
    filter_yaml(yaml_data, fParam)

    # Write YAML to output file
    with open(output_file, 'w') as f:
        yaml = YAML()
        yaml.indent(mapping=4, sequence=4, offset=2)
        yaml.dump(yaml_data, f)



processYaml("input_minimal.yaml", "modbus_sungrow_1_inv_SHxRT_basic_Eth.yaml", ['1', 'SHxRT', 'basic', 'Eth'])
processYaml("input_minimal.yaml", "modbus_sungrow_2_inv_SHxRT_basic_batter_WiNet_WLAN.yaml", ['2', 'SHxRT', ['basic', 'battery'], 'WiNet_WLAN'])
