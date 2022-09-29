## liver registration 

藉由肝臟的定位來推算出前後兩次CT影像中腫瘤位置校正，及觀察其變化，有助於幫助醫生辨別、追蹤腫瘤的情況

權重下載:

https://mega.nz/folder/tdxDVKTa#SJXsGdLlcRyRMEv7UlMugA

https://mega.nz/folder/UUQgiTaT#sgj-8phcMy3p5JVvlm3U6w

https://mega.nz/folder/sJxkVL4J#DY2aJ5BhrtKkOB16hfUHdA

input:

前後ct影像的nii.gz檔

output:

registration得出的轉移矩陣、為移量、縮放量，

def result2plot:預測出的肝臟和mask存成nii.gz並以圖表的方式呈現，也將registration的結果成pcd檔(會消耗時間若只要registration結果可以註解掉)

補充:19,20行改成自己的資料位置


    python full_liver_registration.py

以下是input資料改成dcm版本

input:

前後ct影像的dcm檔

output:

registration得出的轉移矩陣、為移量、縮放量，

def result2plot:預測出的肝臟和mask存成nii.gz並以圖表的方式呈現，也將registration的結果成pcd檔(會消耗時間若只要registration結果可以註解掉)

補充:19,20行改成自己的資料位置


    python full_liver_registration_dcm.py

## 檢視結果

輸入座標example:15,244,123，透過矩陣輸出新座標，可重複輸入直道輸入'c'程式停止執行

    python registrtion_result.py

## 分開功能

## 肝臟偵測

input:data(nii.gz格式)放入"dicom/"資料夾中

output:含有肝臟範圍的dicom以nii.gz檔輸出

    python liver_detection.py
    
## 肝臟分割

input:含有肝臟範圍dicom(nii.gz格式)放入"dicom_detection/"資料夾中

output:肝臟的遮罩以nii.gz檔輸出

    python liver_segmentation.py
    
## 肝臟定位

### 預處理

input:肝臟的遮罩(nii.gz格式)放入"predict_mask/"資料夾中

output:肝臟遮罩的點雲格式

    python mask_to_pointcloud.py

###定位

input:肝臟遮罩的點雲(txt格式) before_mask.txt,after_mask.txt

output:轉移矩陣、為移量、縮放量

    python liver_registration.py
