import numpy as np

tranform_matrix_rot=np.loadtxt("result/transform_matrix_rot.txt")
tranform_matrix_t=np.loadtxt("result/transform_matrix_t.txt")
scale=np.loadtxt("result/scale.txt")

while(1):
    input_index=input("nodule index = ").split(",")  
    if input_index[0]=='c':
        break
    output_index=(np.dot([int(input_index[0]),int(input_index[1]),int(input_index[2])],tranform_matrix_rot)+tranform_matrix_t)*scale
    output_index=[ round(i) for i in output_index]
    print(output_index)

