# Termux Compilation Pitfalls

## NumPy Installation
- Python 3.13+ on Termux has no pip-installable numpy wheels
- **Fix**: Download manylinux aarch64 wheel manually, rename platform tag to `android_30_arm64_v8a`:
  ```bash
  curl -LO https://files.pythonhosted.org/packages/.../numpy-2.5.0-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl
  mv numpy-*-manylinux_*.whl numpy-*-android_30_arm64_v8a.whl
  pip install numpy-*-android_30_arm64_v8a.whl
  ```
- `manylinux` wheels often work on Android because bionic is ABI-compatible with manylinux glibc
- `musllinux` wheels do NOT work (different libc)

## Apt/SSL Certificate Failures
- Termux repos (termux.net) sometimes have SSL cert verification failures
- **Workaround**: Use `its-pointless` repo:
  ```bash
  curl -LO https://its-pointless.github.io/setup-pointless-repo.sh && bash setup-pointless-repo.sh
  pkg install numpy  # from its-pointless extras
  ```

## CMake/Clang Compilation on Termux
- Clang 21 is available and supports C++20
- `libicu` and `capstone` packages available via `pkg install`
- Capstone headers at `/data/data/com.termux/files/usr/include/capstone/capstone.h` (subdirectory)
- CMake `FindPkgConfig` correctly identifies capstone but `CAPSTONE_INCLUDEDIR` points to parent — use `CAPSTONE_INCLUDE_DIRS` instead
- Android-specific: need to link `-llog` for `__android_log_vprint` (used by Dart VM)
- `-dead_strip` linker flag is macOS-only; causes warning but not error on Linux/Android
