import grpc, sys
try:
    from grpc_reflection.v1alpha import reflection_pb2 as rp, reflection_pb2_grpc as rg
except ImportError:
    from yagrc import reflection_pb2 as rp, reflection_pb2_grpc as rg
from google.protobuf import descriptor_pb2 as d
tgt, out = sys.argv[1], sys.argv[2]
stub = rg.ServerReflectionStub(grpc.insecure_channel(tgt))
def ask(**kw):
    return next(stub.ServerReflectionInfo(iter([rp.ServerReflectionRequest(**kw)]), timeout=10))
svcs = [s.name for s in ask(list_services="").list_services_response.service]
files, todo = {}, []
for s in svcs:
    todo += ask(file_containing_symbol=s).file_descriptor_response.file_descriptor_proto
while todo:
    fd = d.FileDescriptorProto.FromString(todo.pop())
    if fd.name in files: continue
    files[fd.name] = fd
    for dep in fd.dependency:
        if dep not in files:
            try: todo += ask(file_by_filename=dep).file_descriptor_response.file_descriptor_proto
            except Exception as e: print("dep miss", dep, e, file=sys.stderr)
fds = d.FileDescriptorSet(file=list(files.values()))
open(out, "wb").write(fds.SerializeToString())
print(tgt, "services:", svcs, "files:", len(files), file=sys.stderr)
