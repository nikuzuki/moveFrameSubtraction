'''
    動体検知
    - フレーム差分から動体を検知
    - 感度設定変更可能
    - 範囲設定
'''
# -*- coding: UTF-8 -*-
import sys
import cv2
import numpy as np

# 時刻tのフレーム画像
sorceImg1 = None
# 時刻t+1のフレーム画像
sorceImg2 = None
# 時刻t+2のフレーム画像
sorceImg3 = None

# 認識画像の名前
filename = "./images/image"
filenum = 1


sensi = sys.argv[1] # 引数:動体検知の感度
areamode = sys.argv[2] # 範囲設定
areaXLU = sys.argv[3]   # 左上X座標
areaYLU = sys.argv[4]   # 左上Y座標
areaXRD = sys.argv[5]   # 右下X座標
areaYRD = sys.argv[6]   # 右下Y座標

areaXLU = int(areaXLU)
areaYLU = int(areaYLU)
areaXRD = int(areaXRD)
areaYRD = int(areaYRD)
color = (0, 0, 0)

# カメラからキャプチャ
cap = cv2.VideoCapture(0)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
print(height, width)
if(int(areaXRD) == 0):
    areaXRD = int(width)

if(int(areaYRD) == 0):
    areaYRD = int(height)

while(cap.isOpened()):
    ret, frame = cap.read()

    sorceImg3 = sorceImg2
    sorceImg2 = sorceImg1
    sorceImg1 = frame

    if sorceImg3 is not None:

        # sorceImg1とsorceImg2との差分を求める(各要素の差分)
        diffImg1_2 = cv2.absdiff(sorceImg1, sorceImg2)

        # sorceImg2とsorceImg3との差分を求める
        diffImg2_3 = cv2.absdiff(sorceImg2, sorceImg3)

        # diffImg1_2とdiffImg2_3の差分を2値化 (thresholdの返り値は2つなので1つだけに)
        diffImg1_2b = cv2.threshold(diffImg1_2, 20, 255, cv2.THRESH_BINARY)[1]
        diffImg2_3b = cv2.threshold(diffImg2_3, 20, 255, cv2.THRESH_BINARY)[1]

        # 二値化された差分画像の共有部分を取得
        andImg = cv2.bitwise_and(diffImg1_2b, diffImg2_3b)

        # 膨張/収縮処理用の配列(uint8は符号なし8bit整数型)
        operator = np.ones((3, 3), np.uint8)

        # 収縮処理 contraction
        ctImg = cv2.erode(andImg, operator, iterations = 1)

        # 膨張処理
        dilateImg = cv2.dilate(ctImg, operator, iterations = 1)

        # フレーム差分結果
        resultImg = cv2.bitwise_and(sorceImg2, dilateImg)
        cv2.imshow("resultImg", resultImg)

        # 範囲設定より検出を行うエリアの絞込み
        if(int(areamode) == 1):

            cv2.rectangle(resultImg, (0, 0), (int(width), areaYLU), color, -1) #上部制限

            cv2.rectangle(resultImg, (0, areaYLU), (areaXLU, int(height)), color, -1) #左部制限
            cv2.rectangle(resultImg, (areaXRD, areaYLU), (int(width), int(height)), color, -1) #右部制限
            cv2.rectangle(resultImg, (areaXLU, areaYRD), (areaXRD, int(height)), color, -1) #下部制限

            cv2.imshow("newResultImg", resultImg)


        grayImg = cv2.cvtColor(resultImg, cv2.COLOR_BGR2GRAY)

        # ラベリング処理 ラベルの数, 画像のラベリング結果, 各ラベルを包括する矩形, 各ラベルの重心
        labelnum, labelimg, contours, GoCs = cv2.connectedComponentsWithStats(grayImg)

        #cv2.imshow("grayImg", grayImg)
        cv2.rectangle(frame, (areaXLU, areaYLU), (areaXRD, areaYRD), (0, 0, 255), 1)
        cv2.imshow("frame", frame)

        # ラベリング処理の結果から最も大きいラベルのみ色塗りを行う
        maxLabel = 0
        maxLabelNum = 0
        for i in range(1, labelnum):
            if maxLabel < contours[i][4]:   # 最も大きいラベル
                maxLabel = contours[i][4]
                maxLabelNum = i

        if maxLabelNum != 0:    # 大きなラベルが存在したら
            if maxLabel > int(sensi):  # そのラベルの画素数がsensiを超えていたら
                print("DP")
                cv2.imwrite(filename + str(filenum) + ".jpg", frame)
                print(sensi)
                filenum += 1
                DPImage = frame

                centerX = int(GoCs[maxLabelNum][0])
                centerY = int(GoCs[maxLabelNum][1])
                print(centerX, centerY)

                cv2.circle(DPImage, (centerX, centerY), 50, (0, 255, 0), 3)
                cv2.rectangle(DPImage, (areaXLU, areaYLU), (areaXRD, areaYRD), (0, 0, 255), 1)
                cv2.imshow("Detection Point", DPImage)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
