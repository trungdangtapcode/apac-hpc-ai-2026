"""Offline protocol and PTY-input tests for iris_bridge; no SSH is opened."""

import ast
import base64
import hashlib
import json
import re
import unittest

import pexpect

import iris_bridge


def make_frame(value, nonce="a1b2c3"):
    payload = json.dumps(value, ensure_ascii=False, allow_nan=False,
                         separators=(",", ":")).encode("utf-8")
    encoded = base64.b64encode(payload).decode("ascii")
    chunks = [encoded[i:i + iris_bridge.OUTPUT_CHUNK_CHARS]
              for i in range(0, len(encoded), iris_bridge.OUTPUT_CHUNK_CHARS)]
    lines = [("__IRIS_JSON_BEGIN__ nonce=%s bytes=%d chunks=%d sha256=%s" %
              (nonce, len(payload), len(chunks), hashlib.sha256(payload).hexdigest())).encode()]
    lines.extend(("__IRIS_JSON_CHUNK__ nonce=%s index=%d data=%s" %
                  (nonce, index, chunk)).encode() for index, chunk in enumerate(chunks))
    lines.append(("__IRIS_JSON_END__ nonce=" + nonce).encode())
    return lines


class FakeChild:
    def __init__(self, data, split=137):
        self.parts = [data[i:i + split] for i in range(0, len(data), split)]

    def read_nonblocking(self, size, timeout):
        if not self.parts:
            raise pexpect.TIMEOUT("fixture exhausted")
        return self.parts.pop(0)


class IrisBridgeTests(unittest.TestCase):
    def test_round_trip_and_crlf_prompt(self):
        nonce = "a1b2c3"
        value = {"hostname": "login02", "unicode": "hồ chí minh", "count": 7}
        transcript = (b"gateway banner\r\n" + b"\r\n".join(make_frame(value, nonce))
                      + b"\r\n\x1b[01;32mrdmaworkshop30@login02\x1b[0m:~$ ")
        got = iris_bridge._read_frame_and_prompt(FakeChild(transcript), nonce,
                                                 __import__("time").monotonic() + 2)
        self.assertEqual(got, value)

    def test_prompt_with_terminal_bell_and_ansi_modes(self):
        prompt = b"banner\x07\x1b[?2004h\x1b[01;32mrdmaworkshop30@login01\x1b[00m:~$ "
        self.assertIsNotNone(iris_bridge._IRIS_PROMPT.search(prompt))

    def test_large_reply_round_trip(self):
        nonce = "d00df00d"
        value = {"text": "x" * 50000}
        self.assertEqual(iris_bridge._parse_frame(make_frame(value, nonce), nonce), value)

    def test_input_uses_short_base64_lines(self):
        nonce = "01" * 16
        body = "result = {'data': " + repr("λ" * 12000) + "}"
        lines = iris_bridge._wire_lines(body, nonce)
        self.assertTrue(all(len(line) <= 1000 for line in lines))
        begin = lines.index("_parts = (") + 1
        end = lines.index(")", begin)
        parts = [ast.literal_eval(line.strip().rstrip(",")) for line in lines[begin:end]]
        self.assertEqual(base64.b64decode("".join(parts)).decode("utf-8"), body)

    def test_rejects_duplicate_chunk(self):
        nonce = "010203"
        lines = make_frame({"ok": True}, nonce)
        lines.insert(2, lines[1])
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._parse_frame(lines, nonce)

    def test_rejects_out_of_order_chunk(self):
        nonce = "010203"
        lines = make_frame({"text": "z" * 2500}, nonce)
        lines[1], lines[2] = lines[2], lines[1]
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._parse_frame(lines, nonce)

    def test_rejects_chunk_before_header(self):
        nonce = "010203"
        lines = make_frame({"ok": True}, nonce)
        lines.insert(0, lines[1])
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._parse_frame(lines, nonce)

    def test_rejects_invalid_digest(self):
        nonce = "010203"
        lines = make_frame({"ok": True}, nonce)
        lines[0] = re.sub(rb"sha256=[0-9a-f]{64}", b"sha256=" + b"0" * 64, lines[0])
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._parse_frame(lines, nonce)

    def test_rejects_malformed_json_even_with_valid_hash(self):
        nonce = "010203"
        payload = b"{bad json}"
        encoded = base64.b64encode(payload).decode("ascii")
        lines = [("__IRIS_JSON_BEGIN__ nonce=%s bytes=%d chunks=1 sha256=%s" %
                  (nonce, len(payload), hashlib.sha256(payload).hexdigest())).encode(),
                 ("__IRIS_JSON_CHUNK__ nonce=%s index=0 data=%s" % (nonce, encoded)).encode(),
                 ("__IRIS_JSON_END__ nonce=" + nonce).encode()]
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._parse_frame(lines, nonce)

    def test_rejects_frame_marker_after_end(self):
        nonce = "010203"
        lines = make_frame({"ok": True}, nonce)
        lines.append(lines[0])
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._parse_frame(lines, nonce)

    def test_rejects_frame_without_prompt(self):
        nonce = "010203"
        transcript = b"\r\n".join(make_frame({"ok": True}, nonce)) + b"\r\n"
        with self.assertRaises(iris_bridge.IrisBridgeError):
            iris_bridge._read_frame_and_prompt(FakeChild(transcript), nonce,
                                               __import__("time").monotonic() + 1)


if __name__ == "__main__":
    unittest.main()

