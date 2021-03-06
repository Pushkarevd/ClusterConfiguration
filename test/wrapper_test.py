from parallel_api.api.client_endpoint import ClientEndpoint
from parallel_api.api.wrapper import cluster_function
from datetime import datetime

endpoint = ClientEndpoint(51353)


@cluster_function(endpoint=endpoint)
def batch_factorial(batch):
    result = 1
    for i in batch:
        result *= i
    return result


batches = [range(i, i + 10000) for i in range(1, 1_000_000, 10000)]

now = datetime.now()

lazy_result = [batch_factorial(batch) for batch in batches]
result = [batch.result for batch in lazy_result]
batch_factorial(result).result
after = datetime.now()

print(f'Local Cluster Result - {after - now}')