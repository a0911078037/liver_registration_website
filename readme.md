## liver registration 

藉由肝臟的定位來推算出前後兩次CT影像中腫瘤位置校正，及觀察其變化，有助於幫助醫生辨別、追蹤腫瘤的情況

input:

前後ct影像的nii.gz檔

output:

registration得出的轉移矩陣、為移量、縮放量

補充:19,20行改成自己的資料位置


    python full_liver_registration.py

 
