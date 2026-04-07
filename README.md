# ds4_pc

DUALSHOCK 4 を Bluetooth 接続し、HID レポートをそのまま表示する最小 CLI ツールです。

## 実装計画

1. `uv` で仮想環境を作る。
2. `hidapi` で DUALSHOCK 4 を HID デバイスとして列挙する。
3. 選択したデバイスを開き、生の入力レポートをそのまま表示する。
4. まずは入力が読めることだけを確認し、その後に必要ならパースやマッピングへ進む。

## セットアップ

```bash
source .venv/bin/activate
uv sync
```

## 使い方

```bash
ds4-pc list-devices
```

Bluetooth 経由で見えている DUALSHOCK 4 を JSON で列挙します。

例:

```json
{"index": 0, "vendor_id": "0x54c", "product_id": "0x5c4", "product": "DUALSHOCK 4 Wireless Controller", "manufacturer": "", "serial_number": "", "transport": "Bluetooth", "usage_page": 1, "usage": 5, "interface_number": null, "path": "IOService:/..."}
```

入力をそのままダンプするには次を実行します。

```bash
ds4-pc dump --device-index 0
```

押したときだけ、HID レポートを JSON で出します。

出力例:

```json
{"length": 78, "hex": "11 c0 7f 80 ...", "bytes": [17, 192, 127, 128]}
```

同じレポートも毎回見たいときは `--show-all` を付けてください。

```bash
ds4-pc dump --device-index 0 --show-all
```

マッピング済み辞書からさらに 8 バイトの独自インターフェースへ詰めた出力を見たいときは次を使います。

```bash
ds4-pc dump --device-index 0 --compact --map-file ds4_map.json --interface-file ds4_compact_interface.json
```

手動でマッピング表を作る場合のひな型は [examples/ds4-hid-report-template.toml](/Users/jinaoyagi/workspace/personal/ds4_pc/examples/ds4-hid-report-template.toml) に置いてあります。`[[bindings]]` ごとに `byte` `mask` `values/threshold` `key` を持つので、そのまま機械処理しやすい形です。

## 補足

- まずは「レポートが読める」ことだけに絞った最小実装です。
- ここで入力が読めたら、次の段階でボタン名へのパースやキー割り当てを足せます。
