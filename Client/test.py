import time
import sys
from ast import literal_eval as make_tuple

ports2Check = list(make_tuple(sys.argv[1]))
ports2Check = map(lambda x: int(x), ports2Check)

# for port in ports2Check:
#     print(port)
#     sys.stdout.flush()
#     time.sleep(0.1)

for i in range(10):
    print("HELLO %d.%d" % divmod(i, 10))
    print('('+str(i)+'/10)')
    sys.stdout.flush()
    time.sleep(0.1)
