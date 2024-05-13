import json


def get_agent_details(json_data:dict)->dict:
    """ Converts the data to agent usable format

    Args:
        json_data (dict): json formatted data with usecase configarations

    Returns:
        dict: Agent wise usable data
    """
    config_manager=json_data['config_manager']
    prompt_manager=json_data['prompt_manager']
    agent_details=[]
    for agent in config_manager['agents']:
        name=agent['name']
        func_config=convert_to_func_config(agent['tools'])
        agent_details.append({
            "name":name,
            "role":prompt_manager[name]['role'],
            "desc":prompt_manager[name]['base_prompt'],
            "instruction_prompt":prompt_manager[name]['instruction_prompt'] if 'instruction_prompt' in prompt_manager[name] else 'string',
            "output_prompt": prompt_manager[name]['output_prompt'] if 'output_prompt' in prompt_manager[name] else 'string',
            "func_config":func_config,
            "tools":get_tools(agent['tools'])
        })
    return agent_details

def get_tools(tool_data:dict) ->list:   
    
    return [tool['tool_name'] for tool in tool_data]

def convert_to_func_config(tool_data:dict)->dict:
    """Convert tools details into Agent usable format

    Args:
        tool_data (dict): tool details

    Returns:
        dict: returns in format of {
            tool_name: {
                args:{},
            }
        }
    """
    config_dict={}
    for tool in tool_data:
        config_dict[tool['tool_name']]={
            "default_args":{t['name']:t['value'] for t in tool['fields'] if len(t)>0},
        }
    return config_dict