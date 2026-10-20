import grpc, sys, json
from yagrc import reflector
from google.protobuf.json_format import MessageToDict
READS = """get_device_info get_history get_log get_network_interfaces get_ping get_status get_location get_persistent_stats
get_connections get_speedtest_status get_radio_stats time dish_get_context dish_get_obstruction_map dish_get_emc dish_get_config
dish_get_rssi_scan_result wifi_get_clients wifi_get_ping_metrics wifi_get_config wifi_guest_info wifi_get_firewall
wifi_backhaul_stats wifi_get_traceroute_status transceiver_get_status transceiver_get_telemetry get_diagnostics
get_gnss_measurement toggle_mode_status get_next_id""".split()
tgt, outdir = sys.argv[1], sys.argv[2]
ch = grpc.insecure_channel(tgt); r = reflector.GrpcReflectionClient(); r.load_protocols(ch, symbols=["SpaceX.API.Device.Device"])
Req = r.message_class("SpaceX.API.Device.Request"); stub = r.service_stub_class("SpaceX.API.Device.Device")(ch)
for c in READS:
    q = Req(); getattr(q, c).SetInParent()
    if c == "get_location": q.get_location.source = 0
    try:
        resp = stub.Handle(q, timeout=10); d = MessageToDict(resp)
        json.dump(d, open(f"{outdir}/{c}.json","w"), indent=1)
        print(f"OK   {c:28} {len(json.dumps(d))}B")
    except grpc.RpcError as e:
        print(f"{e.code().name[:4]} {c:28} {e.details()[:70]}")
