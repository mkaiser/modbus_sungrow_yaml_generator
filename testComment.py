#!/usr/bin/env python3

import ruamel.yaml
import copy


input_file = "input_minimal.yaml"
output_file = "output_testComment.yaml"

# Read YAML with comments
yaml_obj = ruamel.yaml.YAML(typ='rt')
with open(input_file, 'r') as file:
    yaml_data = yaml_obj.load(file)


print("parsed yaml: \n", yaml_data, "\n\n")


filtered_data = copy.deepcopy(yaml_data)



# Write YAML back with comments
with open(output_file, 'w') as file:
    yaml_obj.indent(mapping=4, sequence=4, offset=2)
    yaml_obj.dump(filtered_data, file)

print(f"YAML file '{input_file}' has been read and written to '{output_file}' with comments preserved.")
