from langchain_core.utils.function_calling import convert_to_openai_function,convert_to_openai_tool
import inspect 
import collections 
import json

# use getargspec() 
def clean_desc(desc):
    desc=desc.replace("->","")
    return desc[desc.index("-")+1:]

def arg_to_fields(params,sig_def,required):
    mapping={'string':"text","integer":"number"}
    
    pp_list=[]
    for p in params:
        
        if 'enum' in params[p]:
            
            pp_list.append({
                "name": p,
                "desc":params[p]['description'],
                "type":"selectbox",
                "value": params[p]['enum'],
                "isMandatory":True if p in required else False
            })
        else:
            pp_list.append({
                "name": p,
                "desc":params[p]['description'],
                "type":mapping[params[p]['type']],
                "value": params[p]['default'] if 'default' in params[p] else sig_def[p],
                "isMandatory":True if p in required else False
            })
    return pp_list
def extract_from_sig(sig):
    sig=sig.strip()
    if not sig.startswith("*") or not sig.startswith("**"):
        arg_v=None
        if "=" in sig:
            arg_k,arg_v=sig.split("=")
            if ":" in arg_k:
                
                arg_k=arg_k.split(":")[0]
        else:
            arg_k=sig.split(":")[0]
        return {arg_k:arg_v}
    else:
        return ""
        
def get_args_and_defaults(func):
    signature=str(inspect.signature(func))
    signature=signature[:signature.index(")")]
    signature=signature.strip("(")
    signaturedef=[extract_from_sig(sig) for sig in signature.split(",") if extract_from_sig(sig)!=""]
    s_dict={}
    for f in signaturedef:
        s_dict.update(f)
    return s_dict
    
def convert_tool_into_master_schema(toolSchema):
    signaturedef=get_args_and_defaults(toolSchema.func)
    schema=convert_to_openai_function(toolSchema)
    tool_schema={
        'tool_name':schema['name']
    }
    tool_schema['tool_desc']=clean_desc(schema['description']).strip()
    tool_schema['fields']=arg_to_fields(schema['parameters']['properties'],sig_def=signaturedef,required=schema['parameters']['required'])
    
    return json.dumps(tool_schema, indent=4)
    
    