---
name: flutter-reverse-engineering
description: "Reverse engineer Flutter/Dart APKs using Blutter on Termux/Android — extract API endpoints, Firebase configs, auth flows, and hardcoded secrets from libapp.so."
version: 1.0.0
platforms: [linux, android-termux]
metadata:
  hermes:
    tags: [reverse-engineering, flutter, dart, blutter, apk, android, security]
---

# Flutter/Dart Reverse Engineering

## When to use
- User wants to extract APIs, endpoints, secrets, or auth flows from a Flutter APK
- User asks to reverse engineer a Dart/Flutter mobile app
- User wants to use Blutter to analyze `libapp.so`
- User wants to find hardcoded Firebase configs, API keys, or endpoints

## Prerequisites
- Termux on Android (or Linux with C++20 compiler: g++>=13 or Clang>=16)
- `cmake`, `ninja`, `libicu`, `capstone` installed
- Python 3 with `pyelftools` and `requests`

## Workflow

### 1. Clone Blutter
```bash
git clone https://github.com/worawit/blutter.git ~/blutter
```

### 2. Extract libapp.so from APK
```bash
# APK is just a zip
unzip -o ~/target.apk -d ~/target_extract/
# Find arm64 libapp.so
find ~/target_extract/lib -name "libapp.so"
# Typically at: lib/arm64-v8a/libapp.so
```

### 3. Install Dependencies
```bash
# Termux
pkg install cmake ninja libicu capstone -y
pip install pyelftools requests
```

### 4. Fix Blutter for Termux/Android (CRITICAL)
Two patches needed in `blutter/CMakeLists.txt`:

**Fix 1 — Capstone include path** (line 37):
```
# Wrong:
include_directories(AFTER ${CAPSTONE_INCLUDEDIR})
# Correct:
include_directories(AFTER ${CAPSTONE_INCLUDE_DIRS})
```
`CAPSTONE_INCLUDEDIR` resolves to `/usr/include` (no `capstone/` subdir), but `#include <capstone.h>` needs the subdirectory path.

**Fix 2 — Android log library** (line 46):
```
# Wrong:
target_link_libraries(${BINNAME} PRIVATE ${DARTLIB} capstone)
# Correct:
target_link_libraries(${BINNAME} PRIVATE ${DARTLIB} capstone log)
```
Dart VM references `__android_log_vprint` which requires `-llog`.

### 5. Run Blutter
```bash
cd ~/blutter
python3 blutter.py ~/target_extract/lib/arm64-v8a ~/blutter_out
```
Blutter auto-detects Dart version from flutter engine, downloads Dart SDK, compiles VM, and extracts symbols.

### 6. Extract Information from Output

**Output files:**
| File | Content |
|------|---------|
| `asm/<pkg>/` | Assembly per library with symbols |
| `pp.txt` | Object Pool dump (strings, types, fields) |
| `objs.txt` | Nested Object dump (Firebase config, data structures) |
| `blutter_frida.js` | Frida hooking script |

**Find API endpoints:**
```bash
grep -oP '(?<=String: ")[^"]*(?:/api/|/NewHytoApi/)[^"]*' ~/blutter_out/pp.txt | sort -u
```

**Find Firebase config:**
```bash
grep -B1 -A5 "FirebaseOptions" ~/blutter_out/objs.txt
```

**Find URLs and domains:**
```bash
grep -oP '(?<=String: ")[^"]*(?:https?://|\.co\.id|\.com|firebase)[^"]*' ~/blutter_out/pp.txt | sort -u
```

**Find auth-related strings:**
```bash
grep -oP '(?<=String: ")[^"]*(?:/login|/auth|/token|Bearer|secretKey|password|username)[^"]*' ~/blutter_out/pp.txt | sort -u
```

**Find encryption details:**
```bash
grep -B1 -A5 "AES\|cipher\|PKCS\|secretKey" ~/blutter_out/pp.txt
```

## Extracting Hardcoded Secrets

Flutter apps often embed secrets in `flutter_assets/`. This is the highest-value extraction target.

**Find `.env` files:**
```bash
find ~/target_extract/assets/flutter_assets -name ".env" -o -name "*.env" | xargs cat
```

**Find API keys and secrets in all assets:**
```bash
find ~/target_extract/assets -type f | xargs grep -l "SECRET\|API_KEY\|secretKey\|password\|token" 2>/dev/null
```

**Find encryption keys in Dart source:**
```bash
# AES keys hardcoded in Encrypter class
grep -B2 -A10 "fromUtf8\|Key()" ~/blutter_out/asm/.../encrypter.dart
# Look for strings passed to Encrypted.fromUtf8() — these are the AES keys
```

**Extract Firebase API keys from objs.txt:**
```bash
grep -B1 -A5 "FirebaseOptions\|AIzaSy" ~/blutter_out/objs.txt
```

## Extracting API Payload Structures

The `toJson()` method in each Dart payload class reveals the exact request body structure. These are in the assembly output under `asm/<package>/data/payload/`.

**Find all payload classes:**
```bash
find ~/blutter_out/asm -path "*/payload/*" -name "*.dart" | head -20
```

**Read a payload's toJson() to get request body keys:**
```bash
cat ~/blutter_out/asm/<package>/data/payload/api/auth/login_api_payload.dart
```

The assembly shows each `r17 = "fieldName"` followed by `StoreField` — these are the JSON keys. The `List(N)` constant before `Map._fromLiteral()` shows the key/value types.

**Example — login payload from assembly:**
```
r17 = "userName"    → key: userName
r17 = "password"    → key: password
r17 = "secretKey"   → key: secretKey
```

**Find HTTP methods (GET/POST/PUT):**
The `RequestType` enum values map to Dio methods:
- `Instance_RequestType@a82da1` at offset `#0xc8` → look up which enum value
- Or search `_invoke()` in `api_service.dart` — the switch on `x1` values 0-4 maps to GET/POST/PUT/PATCH/DELETE

## Hitting Extracted APIs with curl

**Full workflow from RE to API testing:**

```bash
# 1. Login to get bearer token
curl -s -X POST \
  'https://BASE_URL/api/User/AuthenticateV2' \
  -H 'Content-Type: application/json' \
  -d '{"userName":"USER","password":"PASS","secretKey":"KEY"}'

# 2. Use token for subsequent requests
curl -s -X POST \
  'https://BASE_URL/api/AttendanceTransaction/InOfficeClock' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer TOKEN' \
  -d '{"clock_in":"ISO8601","datetime":"ISO8601","office":"NAME","remark":"","photo":"","location":{"latitude":-6.0,"longitude":106.0}}'
```

**Tip:** Response field names often differ from request fields. The `AuthMapper`/`SuccessMessageMapper` in `asm/.../mapper/` shows how responses are parsed.

## Pitfalls
1. **Capstone include path**: `CAPSTONE_INCLUDEDIR` vs `CAPSTONE_INCLUDE_DIRS` — Termux puts headers in a subdirectory
2. **Missing `-llog`**: Android logging library not linked by default; causes undefined symbol error at link time
3. **Build time**: Dart VM compilation is slow (~5-10 min on phone). Let `ninja` resume from partial builds — don't re-run from scratch
4. **Dart version mismatch**: Blutter only works with recent Dart versions. Old Flutter apps may not be supported
5. **ARM64 only**: Blutter currently only supports `arm64-v8a` libapp.so
6. **SECRET_KEY in .env**: Many Flutter apps embed `SECRET_KEY` directly in `flutter_assets/.env` — check this FIRST before trying to reverse crypto
7. **`_getValueOrData` pattern**: Config values accessed via `_getValueOrData("KEY_NAME", map)` — trace the map back to find where it's populated (usually `Config.getInstance()` or `flutter_dotenv`)

## References
| File | Content |
|------|---------|
| `references/termux-compilation.md` | Termux-specific compilation pitfalls: numpy wheel install, SSL cert failures, CMake/Clang quirks |
| `references/persona-v2.2.6-case-study.md` | Full case study: reverse engineering BSI Persona v2.2.6 — Firebase config, 35+ API endpoints, AES encryption, auth flow, `.env` secrets extraction |

## Links
- Blutter repo: https://github.com/worawit/blutter
- Output location: `~/blutter_out/`
