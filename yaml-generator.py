#!/usr/bin/env python3
from ruamel.yaml import YAML
from collections import OrderedDict
from ruamel.yaml.comments import CommentedMap
import copy

def filter_yaml(yaml_data, fParam):

    function_registry = OrderedDict(
            {
            'inverter': inverter_check_function,
            'model':model_check_function, 
            'level':level_check_function, 
            'connection': connection_check_function,
        }
    )

    filtered_data = copy.deepcopy(yaml_data)

    for key, value in fParam.items():
        current_variable = key # 'inverter'
        current_value = value # 1
        current_check_function = function_registry[key] # inverter_check_function

        def filter_node(node):
            if isinstance(node, list):
                filtered_list = [filter_node(item) for item in node]
                filtered_list_2 = [item for item in filtered_list if item is not None]
                return filtered_list_2
            elif isinstance(node, dict):
                if current_variable in node:
                    if current_check_function(node, current_variable, current_value):
                        return node
                    else:
                        return None
                else:
                    new_node = {key: filter_node(value) for key, value in node.items()}
                    new_node_2 = {k: v for k, v in new_node.items() if v is not None}
                    return new_node_2
            return node
    
        filtered_data = {key: filter_node(value) for key, value in filtered_data.items()}
        yaml_data_filtered = {k: v for k, v in filtered_data.items() if v}

    return yaml_data_filtered


def processYaml(input_file, output_file, fParam):
    # Read YAML from input file
    with open(input_file, 'r') as f:
        yaml = YAML()
        yaml_data = yaml.load(f)

    print (type(yaml_data))    
    print("parsed yaml: \n", yaml_data, "\n\n")

    print ("\n\n fParam=", fParam,  "\n\n")
    filtered_data = filter_yaml(yaml_data, fParam)

    # Write YAML to output file
    with open(output_file, 'w') as f:
        yaml = YAML()
        yaml.indent(mapping=4, sequence=4, offset=2)
        yaml.dump(filtered_data, f)

def inverter_check_function(node, current_variable, current_value):
    # node is the yaml node
    # current_variable is 'inverter'
    # current_value = fParam['inverter'] = 1 or 2
    # if node['inverter'] == 1, or whatever was passed into fParam:
    if node[current_variable] == current_value:
        return True
    else:
        return False

def model_check_function(node, current_variable, current_value):
    if node[current_variable] == 'all': # apparently we keep all sensors with model=='all'?
        return True
        
    if node[current_variable] == current_value: # node['model'] == SHxRT or whatever
        return True
    else:
        return False

def level_check_function(node, current_variable, current_value):
    # current_value is a list, like ['basic'] or ['basic', 'battery']
    if node[current_variable] in current_value: # if node['level'] in ['basic', 'battery']
        return True
    else:
        return False

def connection_check_function(node, current_variable, current_value):
    # current_variable = 'connection' 
    # current_value = 'Eth'
    # node['connection'] string might look like "Eth, WiNet-WLAN, WiNet-Eth"
    connection_list = node[current_variable].split(', ') # turn into a list ['Eth', 'WiNet-WLAN', 'WiNet-Eth']
    if current_value in connection_list:
        return True
    else:
        return False

if __name__ == '__main__':

    processYaml(
        input_file="input_minimal.yaml", 
        output_file="modbus_sungrow_1_inv_SHxRT_basic_Eth.yaml",
        fParam= 
        {
            'inverter':1, 
            'model':'SHxRT', 
            'level':['basic'], 
            'connection': 'Eth'
        }
    )

    processYaml(
            "input_minimal.yaml", 
            "modbus_sungrow_2_inv_SHxRT_basic_battery_WiNet_WLAN.yaml",
            {
                'inverter':2, 
                'model':'SHxRT', 
                'level':['basic', 'battery'], 
                'connection': 'WiNet-WLAN'
            }
    )

