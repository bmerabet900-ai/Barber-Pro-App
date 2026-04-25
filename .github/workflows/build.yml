name: Build APK
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Buildozer Action
        uses: kivy/buildozer-action@v1
        with:
          python-version: 3.9
