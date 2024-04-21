def check_if_func_call_required(func_name):
    if func_name.startswith("func_"):
        return func_name.strip("func_")