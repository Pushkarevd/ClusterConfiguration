from parallel_api.api.client_endpoint import ClientEndpoint
from parallel_api.api.wrapper import cluster_function


endpoint = ClientEndpoint(51365)


@cluster_function(endpoint=endpoint)
def foo(x, y):
    return x ** 2 + y ** 2


lazy_tasks = [foo(x, x ** .5) for x in range(100)]

results = [x.result for x in lazy_tasks]

print(results)
print(len(results))
