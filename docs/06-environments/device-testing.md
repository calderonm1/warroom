---
title: Device testing (iOS, Android, emulators, device farms)
status: review
owner: ops
last_reviewed: 2026-10-20
related: [docs/03-architecture/globe-rendering.md, docs/06-environments/local-development.md, EP-02, EP-25, OQ-009]
---

# Device testing

## 1. Device matrix

| Role | Device | Source | Use |
| --- | --- | --- | --- |
| iOS reference (high) | **iPhone 18 Pro Max** (owner) | owned | daily on-device testing, ProMotion 120 Hz checks |
| iOS min-spec | iPhone 12 / A14 (iOS 17+) | buy used (cheap) or AWS Device Farm | performance floor |
| Android reference | Pixel 9/10 or Galaxy S24-class | Android Studio emulator + Device Farm | features |
| **Android physical (recommended purchase)** | Mid-range, e.g. Galaxy A55/A56 or Pixel 9a-class | buy | real GPU/thermal behaviour; emulators do not reflect mobile GPU performance |
| Android min-spec | Snapdragon 680 / Helio G85, 4 GB RAM | Device Farm, or a cheap used phone | performance floor |
| Tablets | iPad (10th gen+), Android tablet | simulator/emulator + Device Farm | layout |

## 2. iOS on your iPhone 18 Pro Max

1. Apple Developer Program membership (needed for TestFlight and App Store; an organization account needs a D-U-N-S number, see [open questions](../07-planning/open-questions.md)).
2. Unity: Build Settings, iOS, build to `client/Builds/iOS`, which produces an Xcode project.
3. Xcode: select your team (automatic signing for dev), plug in the iPhone (or use Wi-Fi debugging), Run.
4. Faster loop: Unity **Build and Run** with the device connected; attach the Unity Profiler over USB or Wi-Fi.
5. Distribution to yourself without a cable: TestFlight internal testing (CI uploads on each `main` build once `EP-04` is done).

## 3. iOS Simulator

Xcode's Simulator runs Unity "Simulator SDK" builds (Player Settings, Target SDK, Simulator). Good for UI and layout across screen sizes. **Not valid for GPU performance.**

## 4. Android emulator profiles

`make android-avd` creates the two AVDs below when those names are missing. It does not change an AVD that already exists. Arm64 hosts (Apple Silicon included) get `arm64-v8a` Google APIs system images. x86_64 hosts get `x86_64` images. The command installs a missing system image and answers `y` to the SDK license prompts that install requires.

API 29 is the proposed Android floor in [open questions](../07-planning/open-questions.md) (OQ-009). That question is still open. `wr_small_api29` tracks the proposal already written in the device matrix.

| AVD | Device id | Image | Use |
| --- | --- | --- | --- |
| `wr_pixel_api35` | `pixel_8` | Android 15 (API 35), 4 GB RAM, host GPU (GLES and Vulkan) | reference functional checks |
| `wr_small_api29` | `small_phone` | Android 10 (API 29) | min-spec layout checks |

Emulators are for **functional** testing and layout. Use a physical mid-range device or Device Farm for **performance** sign-off.

### Install the SDK once

1. Install Android Studio (or the command-line tools) and set `ANDROID_HOME` to the SDK root. `sdkmanager` and `avdmanager` must be on `PATH` or under `$ANDROID_HOME/cmdline-tools/latest/bin`.
2. Unity Android Build Support (OpenJDK, SDK and NDK) arrives with `ST-02.3.1`. Until that project exists, Android Studio's SDK is enough to create the AVDs.

### Create

```bash
make android-avd
make android-avd ARGS="--json"   # one JSON object; exit status is non-zero on failure
```

A missing SDK prints an error that names this section.

### Launch and install a development build

Reference (`wr_pixel_api35`):

```bash
emulator -avd wr_pixel_api35
```

Wait until the home screen is up, then either:

1. Unity: Build Settings, Android, IL2CPP, ARM64 on arm64 hosts (x86_64 on x86 hosts). Select `wr_pixel_api35`. **Build And Run**.
2. Or install an APK you already built: `adb install -r client/Builds/Android/<name>.apk`, then open the app from the launcher.

Min-spec layout (`wr_small_api29`):

```bash
emulator -avd wr_small_api29
```

Use the same install path with this AVD selected. Use it for layout, not GPU performance.

Logs on either AVD: `adb logcat -s Unity`. Profiling: Unity Profiler (autoconnect) and Android GPU Inspector on physical devices.

## 5. Cloud device farms

| Service | Use |
| --- | --- |
| **AWS Device Farm** (aligned with AWS) | Automated smoke and perf runs on a matrix of real iOS and Android devices before each milestone; remote access sessions for manual checks |
| Firebase Test Lab | Alternative for Android-only matrix runs |

An automated device smoke test (boot, connect to staging, open globe, pan/zoom, record fps and memory) is story `ST-25.2.2`.

## 6. If you do not have a Mac

- iOS builds: GitHub Actions macOS runners (CI) or a cloud Mac (AWS EC2 Mac has a 24-hour minimum allocation, so it's costly for occasional use; MacStadium or Scaleway Mac mini are alternatives).
- You can still develop gameplay in the Unity Editor on Windows or Linux and test on the iPhone via TestFlight builds from CI.
