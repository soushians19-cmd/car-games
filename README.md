# Car Dodge — Android game source

A simple top-down car-dodging game written in Python + Kivy, with a
settings screen (graphics quality, difficulty) and touch controls.
This is **source code**, not an APK — I can't compile a real APK
myself (no Android build tools in this environment), so below are
two ways to turn it into one.

## Option A — Build in the cloud (recommended, most reliable)

Compiling Android apps needs several GB of SDK/NDK tools; doing this
directly on a phone in Termux often fails or takes hours. The
included `.github/workflows/build.yml` lets GitHub build the APK
for you for free:

1. Create a new GitHub repo and upload all these files to it
   (keep the folder structure, including the hidden `.github` folder).
2. Push to the `main` branch (or open the repo → Actions tab →
   run the "Build APK" workflow manually).
3. Wait for the workflow to finish (10–20 minutes the first time).
4. Open the finished run → **Artifacts** → download `car-dodge-apk`.
   Unzip it, transfer the `.apk` to your phone, and install it
   (you'll need to allow "install unknown apps" for whatever app
   you use to open it).

No Android Studio, no local build tools needed — everything happens
on GitHub's servers.

## Option B — Build directly with Termux (harder, can be flaky)

This compiles on-device with `buildozer`. It needs ~4 GB free
storage, a stable network, and can take a long time on a phone.

```bash
pkg update && pkg upgrade
pkg install python git build-essential libffi openssl clang cmake \
    unzip zip which
pip install --upgrade pip buildozer cython==0.29.33

# get the source onto the phone (however you prefer — git clone,
# or transfer the files into this folder), then:
cd car_game
buildozer android debug
```

The finished APK appears in `car_game/bin/`. If the build fails
partway (common cause: Termux's package set is slightly different
from a full Linux distro), the error message usually names the
missing tool — install it with `pkg install <name>` and re-run
`buildozer android debug`.

## Testing on desktop first (optional)

Before building for Android, you can just run it as a normal
Python app to check the gameplay:

```bash
pip install kivy
python main.py
```

## What's included

- `main.py` — the game: menu, settings (graphics quality: Low/Medium/High,
  difficulty: Easy/Normal/Hard), and the dodge-the-obstacles gameplay
  with touch/tap steering.
- `buildozer.spec` — Android packaging config (app name, permissions,
  min/target API).
- `.github/workflows/build.yml` — cloud build pipeline (Option A).

Feel free to ask me to add things — power-ups, a highscore file,
different car sprites, sound, etc. — before you build it.
