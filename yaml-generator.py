#!/usr/bin/env python3

import ruamel.yaml
from collections import OrderedDict
import copy


# ToDo:
# - preserve comments (e.g. file header of modbus_sungrow.yaml)
#   - low prio add current date to file header
# comment out every key which is part of fParam (inverter, model, level, connection)
# makes debugging easier and the resulting yaml files can be parsed by Home assistant 

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
    # return --> yaml file is just  "null"

    for key, value in fParam.items():
        current_variable = key # 'inverter'
        current_value = value # 1
        current_check_function = function_registry[key] # inverter_check_function

        def filter_node(node): # yaml is a nesting doll of lists and dicts
            if isinstance(node, list): # if the current node is a list
                filtered_list = [filter_node(item) for item in node] # recursively apply this function to each item in the list until we get to a dict
                filtered_list_2 = [item for item in filtered_list if item is not None] # sometimes after recursively applying, we end up with empty items at the top level because the lower ones were filtered out, this removes them
                return filtered_list_2
            elif isinstance(node, dict): # yay, we got to a dict
                if current_variable in node: # if the current variable we are filtering is one of the keys in the dict:
                    if current_check_function(node, current_variable, current_value): # use the current_check_function to check if it should stay.
                        return node # current_check_function returned true, keep the node!!!
                    else:
                        return None # current_check_function returned false, remove the node!!!
                else:
                    new_node = {key: filter_node(value) for key, value in node.items()} # current variable is not in the dict. we recursively apply this function
                    new_node_2 = {k: v for k, v in new_node.items() if v is not None} # sometimes after recursively applying, we end up with empty items at the top level because the lower ones were filtered out, this removes them
                    return new_node_2
            return node
    
        filtered_data = {key: filter_node(value) for key, value in filtered_data.items()}
        yaml_data_filtered = {k: v for k, v in filtered_data.items() if v}

    return yaml_data_filtered


def processYaml(input_file, output_file, fParam):
    # Create a YAML object with "roundtrip" preservation of comments
    yaml_obj = ruamel.yaml.YAML(typ='rt')

    # Read YAML data from the input file
    with open(input_file, 'r') as f:
        yaml_data = yaml_obj.load(f)

    print("parsed yaml: \n", yaml_data, "\n\n")

    print ("\n\n fParam=", fParam,  "\n\n")
    filtered_data = filter_yaml(yaml_data, fParam)

    # Write YAML data to the output file
    with open(output_file, 'w') as f:
        yaml_obj.indent(mapping=4, sequence=4, offset=2)
        # yaml_obj.representer.merge_comments = lambda x, y: None
        yaml_obj.dump(filtered_data, f)

def inverter_check_function(node, current_variable, current_value):
    # node is the yaml node
    # current_variable is 'inverter'
    # current_value = fParam['inverter'] = 1 or 2
    # if node['inverter'] == 1, or whatever was passed into fParam:

    # if fparam['inverter'] = 2, we want to keep all nodes for inverter 1 and 2
    if node[current_variable] <= current_value:  
        return True
    else:
        return False

def model_check_function(node, current_variable, current_value):
    if node[current_variable] == 'all' or current_value == 'all': # keep everything labeled 'all'
        return True
        
    if node[current_variable] == current_value: # node['model'] == SHxRT or whatever
        return True
    else:
        return False

def level_check_function(node, current_variable, current_value):
    # current_value maybe a list, like ['basic'] or ['basic', 'battery']
    level_list = node[current_variable].split(', ') # turn into a list ['basic', 'battery', 'extended']     

    if 'all' in level_list or current_value == 'all': # keep everything labeled 'all'
        return True

    # for (i in current_value.items()):
    #     if i in level_list: 
    #         return True
    # if any (i in level_list for i in current_value):
    if node[current_variable] in current_value: # if node['level'] in ['basic', 'battery']
        return True
    else:
        return False

def connection_check_function(node, current_variable, current_value):
    # current_variable = 'connection' 
    # current_value = 'Eth'
    # node['connection'] string might look like "Eth, WiNet-WLAN, WiNet-Eth"
    connection_list = node[current_variable].split(', ') # turn into a list ['Eth', 'WiNet-WLAN', 'WiNet-Eth']
    
    if current_value == 'all' or 'all' in connection_list: # keep everything labeled 'all'
        return True
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
            'level':['basic', 'extended'], 
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


    processYaml(
            "input_minimal.yaml", 
            "modbus_sungrow_1_inv_SHxRT_all_WiNet_WLAN.yaml",
            {
                'inverter':1, 
                'model':'SHxRT', 
                'level': 'all',
                'connection': 'WiNet-WLAN'
            }
    )    

