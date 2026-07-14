"""
Handler: Tuya endpoint health check + device status + ON/OFF test
"""
import subprocess, sys, json, os

from config import HERMES_DIR


def tuya_test_handler() -> dict:
    """Ping Tuya API: fetch device status. Return result + device info."""
    result = {"ok": False, "device": {}, "error": None}
    plug_path = os.path.join(HERMES_DIR, 'scripts', 'tuya-plug.py')
    if not os.path.isfile(plug_path):
        result["error"] = "tuya-plug.py not found"
        return result

    try:
        out = subprocess.check_output(
            [sys.executable, plug_path], timeout=15
        ).decode()
        data = json.loads(out)
        if data.get("success"):
            result["ok"] = True
            st = {}
            for r in data.get("result", []):
                c = r.get("code", "")
                v = r.get("value")
                if c == "switch_1":
                    st["switch"] = v
                elif c == "cur_voltage":
                    st["voltage"] = f"{v/10:.1f}V"
                elif c == "cur_power":
                    st["power"] = f"{v}W"
                elif c == "cur_current":
                    st["current"] = f"{v}mA"
                elif c in ("add_ele",):
                    st["total_kwh"] = f"{v/100:.3f}kWh"
                elif c.startswith("fault"):
                    st["fault"] = v
            result["device"] = st
        else:
            result["error"] = data.get("msg", "Unknown API error")
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout — endpoint unreachable"
    except json.JSONDecodeError:
        result["error"] = "Invalid API response (not JSON)"
    except Exception as e:
        result["error"] = str(e)

    return result


def tuya_cmd_handler(cmd: str) -> dict:
    """Send ON or OFF command to Tuya plug. Return result."""
    result = {"ok": False, "error": None, "cmd": cmd}
    plug_path = os.path.join(HERMES_DIR, 'scripts', 'tuya-plug.py')
    if not os.path.isfile(plug_path):
        result["error"] = "tuya-plug.py not found"
        return result
    if cmd not in ("on", "off"):
        result["error"] = "Invalid command. Use 'on' or 'off'"
        return result

    try:
        out = subprocess.check_output(
            [sys.executable, plug_path, cmd], timeout=15
        ).decode()
        data = json.loads(out)
        if data.get("success"):
            result["ok"] = True
        else:
            result["error"] = data.get("msg", "API error")
    except subprocess.TimeoutExpired:
        result["error"] = "Timeout"
    except json.JSONDecodeError:
        result["error"] = "Invalid response"
    except Exception as e:
        result["error"] = str(e)

    return result
