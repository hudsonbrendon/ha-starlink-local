import sys
from google.protobuf import descriptor_pb2 as d, descriptor_pool
fds = d.FileDescriptorSet.FromString(open(sys.argv[1],'rb').read())
pool = descriptor_pool.DescriptorPool()
pend = list(fds.file)
while pend:
    for f in list(pend):
        try: pool.Add(f); pend.remove(f)
        except Exception: pass
req = pool.FindMessageTypeByName('SpaceX.API.Device.Request')
for o in req.oneofs:
    for f in o.fields:
        m = f.message_type
        args = ",".join(x.name for x in m.fields) if m else ""
        print(f"{f.number:5} {f.name}({args})")
