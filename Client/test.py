import time
import sys
from ast import literal_eval as make_tuple
import json

# ports2Check = list(make_tuple(sys.argv[1]))
# ports2Check = map(lambda x: int(x), ports2Check)

# for port in ports2Check:
#     print(port)
#     sys.stdout.flush()
#     time.sleep(0.1)

for i in range(10):
    print(json.dumps({'tag': 'progress', 'completed': i, 'total': 10}))
    print(json.dumps(
        {'tag': 'log', 'message': "Testing %d.%d" % divmod(i, 10)}))
    sys.stdout.flush()
    time.sleep(0.1)
