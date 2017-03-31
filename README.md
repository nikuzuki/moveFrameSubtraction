動体検知
===
## Description
- フレーム差分から動体を検知
- ラベリング処理後、最も大きな部分の重心座標を検出
- 感度の設定
- 検出範囲の設定

## Plans
No plans

## Usage
python moveFrameSubtraction_job.py [sensi] [mode(0or1)] [leftupX] [leftupY] [rightdownX] [rightdownY]
mode = 1 : 検出範囲の設定ON

## Author
KOHEI MAKITA(@nikuzuki_29)
