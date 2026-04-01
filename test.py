def add(a, b):
    return a + b

tool_registry = {
    "add": add
}

function_name = "add"
func = tool_registry[function_name]

print(func)          
print(type(func)) 

arguments_dict = {
    "a": 3,
    "b": 5
}

result = func(**arguments_dict)
print(result) 