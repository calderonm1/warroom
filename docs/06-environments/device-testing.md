---
title: Device testing (iOS, Android, emulators, device farms)
status: review
owner: ops
last_reviewed: 2026-10-18
related: [docs/03-architecture/globe-rendering.md, EP-02, EP-25]
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

## 4. Android emulator (no Android phone yet)

1. Android Studio, Device Manager, create AVDs:
   - `wr_pixel_api35`: Pixel 8 profile, Android 15 (API 35), **arm64-v8a image on Apple Silicon** (x86_64 on Intel/AMD hosts), 4 GB RAM, hardware GLES/Vulkan.
   - `wr_small_api29`: small phone profile, Android 10 (API 29), min-spec layout checks.
2. Unity: Android target with **IL2CPP**, ARM64 (+ x86_64 for emulators on x86 hosts). Build and Run with the emulator selected, or `adb install`.
3. Logs: `adb logcat -s Unity`. Profiling: Unity Profiler (autoconnect) and Android GPU Inspector on physical devices.
4. Emulators are fine for **functional** testing. Use a physical mid-range device or Device Farm for **performance** sign-off.

## 5. Cloud device farms

| Service | Use |
| --- | --- |
| **AWS Device Farm** (aligned with AWS) | Automated smoke and perf runs on a matrix of real iOS and Android devices before each milestone; remote access sessions for manual checks |
| Firebase Test Lab | Alternative for Android-only matrix runs |

An automated device smoke test (boot, connect to staging, open globe, pan/zoom, record fps and memory) is story `ST-25.2.2`.

## 6. If you do not have a Mac

- iOS builds: GitHub Actions macOS runners (CI) or a cloud Mac (AWS EC2 Mac has a 24-hour minimum allocation, so it's costly for occasional use; MacStadium or Scaleway Mac mini are alternatives).
- You can still develop gameplay in the Unity Editor on Windows or Linux and test on the iPhone via TestFlight builds from CI.
