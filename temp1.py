import os
import glob

def find_result(self):
    list_file = glob.glob('results/*.mp4')

    print(list_file)

    file_name = os.path.basename('data/wildboar04_gt.avi')

    print(file_name)

    f_list=[]

    for i in list_file:
        file = os.path.basename(i).split('.')[0]    
        if file_name.split('.')[0] in file:        
            f_list.append(i)

    print(f_list[-1])

    
        

