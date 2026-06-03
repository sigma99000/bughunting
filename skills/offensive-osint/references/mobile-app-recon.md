# Mobile App Recon

## Acquire the APK / IPA

```bash
# Android — pull from Play Store via apkpure / similar; never side-load to your phone
# iOS — use ipatool with a valid Apple ID (your own)
```

## Decompile

```bash
# APK
apktool d app.apk
jadx-gui app.apk

# IPA
unzip app.ipa
class-dump <binary>
otool -L <binary>      # list dylibs
```

## What to mine

### Secrets

```bash
grep -rE 'AKIA|sk_live|xoxb|ghp_|AIza' app/
strings <binary> | grep -E '(api[._-]?key|secret|token)'
```

### Endpoints

```bash
grep -rE '(http|https)://[^"]+' app/ | sort -u > endpoints.txt
```

### Deeplinks

Android `AndroidManifest.xml`:

```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW"/>
  <category android:name="android.intent.category.BROWSABLE"/>
  <data android:scheme="example" android:host="open"/>
</intent-filter>
```

Test:

```bash
adb shell am start -a android.intent.action.VIEW -d "example://open/profile?id=victim"
```

Look for: parameter reflection into WebView, intent extras flowing
to deeplink targets without validation, exported activities.

### Certificate pinning

```bash
# Check if app pins certs (good for them, work for you)
grep -rE 'CertificatePinner|trustkit|sslPinning' app/
```

If pinning present, hook with Frida (`fridantipinning.js`) to MITM.
Many pin only on Android `network_security_config.xml` — read it.

### Firebase

```bash
grep -rE 'firebaseio\.com|firebase\.google' app/
```

Test:

```
curl https://<project>.firebaseio.com/.json
# If 200 returns DB content → world-readable Firebase
```

## iOS extras

- `Info.plist` — URL schemes, App Transport Security exceptions
- Embedded `.plist` files containing dev secrets
- Frameworks loaded — out-of-date libs

## See also

- `secret-patterns.md`
- `hunt-auth` — JWT in app strings
- `hunt-ssrf` — deeplink → server-side fetch
