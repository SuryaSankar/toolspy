def set_instance_attr_vals(instance, attr_vals):
    for k, v in attr_vals.items():
        setattr(self, k, v)

def to_dict(instance, recurse=True):
    result = {}
    raw_dict = vars(instance)
    for k, v in raw_dict.items():
        if k != 'self':
            if recurse and hasattr(v, "__dict__"):
                result[k] = to_dict(v)
            else:
                result[k] = v
    return result