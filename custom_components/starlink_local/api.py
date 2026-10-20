"""Thin gRPC client for the Starlink dish and router Device.Handle service.

Both the dish (192.168.100.1:9200) and the WiFi router (192.168.1.1:9000) expose
the same `SpaceX.API.Device.Device` service with gRPC reflection enabled, so we
build the request/stub classes from reflection once and reuse them. No vendored
protos to keep in sync with firmware.
"""
from __future__ import annotations

import grpc
from google.protobuf.json_format import MessageToDict
from yagrc import reflector

SERVICE = "SpaceX.API.Device.Device"


class StarlinkDevice:
    """Blocking gRPC client. Call only from an executor thread."""

    def __init__(self, target: str) -> None:
        self.target = target
        self._channel: grpc.Channel | None = None
        self._req = None
        self._stub = None

    def _connect(self) -> None:
        channel = grpc.insecure_channel(self.target)
        ref = reflector.GrpcReflectionClient()
        ref.load_protocols(channel, symbols=[SERVICE])
        self._req = ref.message_class("SpaceX.API.Device.Request")
        self._stub = ref.service_stub_class(SERVICE)(channel)
        self._channel = channel

    def call(self, command: str, timeout: float = 10.0, **fields) -> dict:
        """Invoke one oneof command, e.g. call("get_status"). Returns a dict."""
        if self._stub is None:
            self._connect()
        request = self._req()
        sub = getattr(request, command)
        sub.SetInParent()
        for key, value in fields.items():
            setattr(sub, key, value)
        try:
            resp = self._stub.Handle(request, timeout=timeout)
        except grpc.RpcError:
            # Drop the channel so the next poll rebuilds it (firmware reboot,
            # WiFi drop, reflection schema bump all heal this way).
            self._channel = self._stub = self._req = None
            raise
        # MessageToDict wraps the reply in {apiVersion, <oneofName>: {...}}.
        # Return the single payload dict, flattened one level.
        data = MessageToDict(resp)
        data.pop("apiVersion", None)
        for value in data.values():
            if isinstance(value, dict):
                return value
        return data
