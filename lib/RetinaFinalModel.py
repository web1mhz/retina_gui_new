import os
import glob
import time
import numpy as np
import cv2
import pandas as pd
from lxml import etree # xml encoding 문제 해결


from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

# --------------------------클래스명 변경----------------------------------
labels_to_names_seq = {0: 'marten',1:'raccoon',2:'waterdeer', 3:'wildboar', 4:'wildcat'} # 포유류 5종 wildlife5_xxxx
# labels_to_names_seq = {0: 'marten',1:'waterdeer', 2:'wildboar', 3:'wildcat'} # 포유류 4종 wildlife4_xxxx
# labels_to_names_seq = {0: 'marten',1:'waterdeer', 2:'wildboar'} # 포유류 3종 wildlife3_xxxx
# labels_to_names_seq = {0: 'raccoon',1:'wildcat'} # 포유류 2종 wildlife2_xxxx
# labels_to_names_seq = {0: 'wildboar'}
# --------------------------클래스명 변경----------------------------------

#################################################학습자료와 검증자료 랜덤선택 #####################################################################
#------------ 폴더에서 리스트를 만들어 생성
def get_train_valid_indexes(anno_path, valid_size):
    
    np.random.seed(0)
    
    xml_files = [xml_file for xml_file in glob.glob(os.path.join(anno_path, '*.xml'))]
    xml_files = np.array(xml_files)
    total_cnt = xml_files.shape[0]
    valid_cnt = int(total_cnt * valid_size)
    
    total_indexes = np.arange(0, total_cnt)
    valid_indexes = np.random.choice(total_cnt, valid_cnt, replace=False)
    train_indexes = total_indexes[~np.isin(total_indexes, valid_indexes)]
    
    return train_indexes, valid_indexes

#------------- 파일에서 리스트를 만들어 생성
def get_train_valid_indexes_from_xml_list(xml_list, valid_size):
    np.random.seed(0)
    
    # xml_files = [xml_file for xml_file in glob.glob(os.path.join(anno_path, '*.xml'))]       
    
    total_cnt = xml_list.shape[0]
    valid_cnt = int(total_cnt * valid_size)
    
    total_indexes = np.arange(0, total_cnt)
    valid_indexes = np.random.choice(total_cnt, valid_cnt, replace=False)
    train_indexes = total_indexes[~np.isin(total_indexes, valid_indexes)]
    
    return train_indexes, valid_indexes

################################################분할비율에 따른 학습자료와 검증자료 생성##############################################

def xml_to_csv_sampling(path, output_filename, sample_index):
    xml_list = np.array([xml_file for xml_file in glob.glob(path + '/*.xml')])
    xml_list = xml_list[sample_index]
    # xml 확장자를 가진 모든 파일의 절대 경로로 xml_file할당. 
    with open(output_filename, "w") as train_csv_file:
        for xml_file in xml_list:
            # xml 파일을 parsing하여 XML Element형태의 Element Tree를 생성하여 object 정보를 추출. 
            tree = ET.parse(xml_file)
            root = tree.getroot()
            # 파일내에 있는 모든 object Element를 찾음. 
            full_image_name = os.path.join(IMAGE_DIR, root.find('filename').text)
            value_str_list = ' '
            for obj in root.findall('object'):
                xmlbox = obj.find('bndbox')
                x1 = int(xmlbox.find('xmin').text)
                y1 = int(xmlbox.find('ymin').text)
                x2 = int(xmlbox.find('xmax').text)
                y2 = int(xmlbox.find('ymax').text)
                # ----------------------------------------------클래스명 변경-----------------------------------------  
                class_name='wildboar'
                # ----------------------------------------------클래스명 변경 끝----------------------------------------- 
                value_str = ('{0},{1},{2},{3},{4},{5}').format(full_image_name,x1, y1, x2, y2, class_name)
                # object별 정보를 tuple형태로 object_list에 저장. 
                train_csv_file.write(value_str+'\n')
        # xml file 찾는 for loop 종료 

################################################################################################################

# 원래 케라스레티나넷에 포함된 visualization.py 파일에 있는 draw_caption(image, box, caption) 기능을 쓰지 않고 다음 함수를 사용함.
def modified_draw_caption(image, box, caption, color):
    """ Draws a caption above the box in an image."""
    b = np.array(box).astype(int)

    # getTextSize(글자, 글꼴, 크기, 두께)
    text_size = cv2.getTextSize(caption, cv2.FONT_HERSHEY_DUPLEX, 1, 1)

    text_length = text_size[0][0]
    text_height = text_size[0][1]

    print(text_size)

    cv2.rectangle(image, (b[0], b[1] - text_height), (b[0] + text_length, b[1]), color, -1)
    cv2.putText(image, caption, (b[0], b[1]), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1)

#############################################################################################################

def get_detected_image_retina(model, img_array, use_copied_array, is_print=True):
    
    # copy to draw on
    draw_img = None
    if use_copied_array:
        draw_img = img_array.copy()
    else:
        draw_img = img_array
    
    img_array = preprocess_image(img_array)
    img_array, scale = resize_image(img_array)
    
    # process image
    start = time.time()

    # 모델 예측
    boxes, scores, labels = model.predict_on_batch(np.expand_dims(img_array, axis=0))


    if is_print:
        print("object detection 처리 시간: ", round(time.time() - start,5))
    
    # correct for image scale
    boxes /= scale
    
    box_cnt = 0
    boxbnd=[]
    accuracy=[]
    target_label=[]
    name=[]
    
    # visualize detections
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < 0.5:
            break

        color = label_color(label)

        b = box.astype(int)
        
        # box 경계 두께 지정
        linewidth = 5
        
        draw_box(draw_img, b, color=color,thickness=linewidth)
        
        score_percent = score * 100

        caption = "{} {:.1f}%".format(labels_to_names_seq[label], score_percent)
        
        acc = "{:.2f}%".format(score_percent)
        
        # draw_caption(draw_img, b, caption)
        modified_draw_caption(draw_img, b, caption, color)
        
        box_cnt+=1

        accuracy.append(acc) #### [99 99]
        target_label.append(label) ### [wild wild]
        name.append(labels_to_names_seq[label]) ### [wild wild]
        boxbnd.append(box) #### [1 1 1 1 2 2 2 2]   

    
    if is_print:
        print("이미지 processing 시간: ", round(time.time() - start,5))
        print(f"탐지된 객체 수는 {box_cnt}개 입니다.")
        print(f" {name} 객체의 탐지정확도는 \n {accuracy} % 입니다.")
        #--------------박스크기-----------------------------------------
        print('boxes is', box)
        #--------------박스크기-----------------------------------------  
    
    return draw_img, box_cnt, name, accuracy, boxbnd

##################################################################################################################################

def detect_video_retina(model, input_path, output_path=""):    
    start = time.time()    
    cap = cv2.VideoCapture(input_path)
    
    codec = cv2.VideoWriter_fourcc(*'XVID')
    vid_fps = cap.get(cv2.CAP_PROP_FPS)
    vid_size= (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    vid_writer = cv2.VideoWriter(output_path, codec, vid_fps, vid_size)
    
    frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('총 Frame 갯수:', frame_cnt)
    total_frame=frame_cnt

    box_cnt_1=[]
    name_1=[]
    accuracy_1=[]
    boxbnd_1=[]
    results=[]
    
    while True:

        hasFrame, image_frame = cap.read()
        if not hasFrame:
            print('프레임이 없거나 종료 되었습니다.')
            break

        detected_image, cnt,  c_name, c_accuracy, c_boxbnd = get_detected_image_retina(model,image_frame, use_copied_array=False, is_print=True)

        print(cnt, "개가 탐지됨")
        box_cnt_1.append(cnt)
        name_1.append(c_name)
        accuracy_1.append(c_accuracy)
        boxbnd_1.append(c_boxbnd)
        results.append([cnt, c_name, c_accuracy, c_boxbnd])

        frame_cnt-=1
        print(f"{frame_cnt}프레임, {frame_cnt/total_frame * 100 : .2f} % 남음")

        vid_writer.write(detected_image)
    
    # df = pd.DataFrame(box_cnt_1)
    # df1 = pd.DataFrame(name_1)
    # df2 = pd.DataFrame(accuracy_1)
    # df3 = pd.DataFrame(boxbnd_1)
    # result = pd.DataFrame(results)    

    # df.to_csv(CNT_FILE_PATH)
    # df1.to_csv(CLASS_NAME_FILE_PATH)
    # df2.to_csv(ACCURACY_FILE_PATH)
    # df3.to_csv(BOXBND_FILE_PATH)
    # result.to_csv(RESULT_FILE_PATH)

    vid_writer.release()
    cap.release()
    lapse_time = round(time.time()-start, 5)
    print('### Video Detect 총 수행시간:', lapse_time)
    min = int(lapse_time / 60)
    second = ((lapse_time / 60) - min) * 60 
    print(f"총 수행시간은 {min}분 {second :.0f}초 걸렸습니다.")

    return results

###############################################################################################################################

def detect_stream_retina(model, input_path, output_path=""):
    
    start = time.time()
    
    cap = cv2.VideoCapture(input_path)
    
    codec = cv2.VideoWriter_fourcc(*'XVID')
    vid_fps = cap.get(cv2.CAP_PROP_FPS)
    vid_size= (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    vid_writer = cv2.VideoWriter(output_path, codec, vid_fps, vid_size)
    
    frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('총 Frame 갯수:', frame_cnt)
    total_frame=frame_cnt

    box_cnt_1=[]
    name_1=[]
    accuracy_1=[]
    boxbnd_1=[]
    results=[]

    i = 0
    
    while True:

        hasFrame, image_frame = cap.read()      
        if not hasFrame:
            print('프레임이 없거나 종료 되었습니다.')
            break
    # -----------------원본 비디오 스트리밍 시작 ---------------------------------------------
        cv2.imshow('frame',image_frame) 

        if cv2.waitKey(1) & 0xFF == ord('q') or hasFrame==False :
            cap.release()
            cv2.destroyAllWindows()
            break
    # ------------------비디오 스트리밍 시작----------------------------------------------

        detected_image, cnt,  c_name, c_accuracy, c_boxbnd = get_detected_image_retina(model,image_frame, use_copied_array=False, is_print=True)

        print(cnt, "개가 탐지됨")

        box_cnt_1.append(cnt)
        name_1.append(c_name)
        accuracy_1.append(c_accuracy)
        boxbnd_1.append(c_boxbnd)

        frame_cnt-=1
        print(f"{frame_cnt}프레임, {frame_cnt/total_frame * 100 : .2f} % 남음")

        
    # ------------------탐지결과 비디오 스트리밍 내가 추가한 내용 ---------------------------------------------
        cv2.imshow('frame1',detected_image)

        if cnt > 0:
            cv2.imwrite(f'temp/test_{i}.jpg', detected_image)
            results.append([cnt, c_name, c_accuracy, c_boxbnd])
    # ------------------탐지결과 비디오 스트리밍-------------------------------------------------------------
        
        vid_writer.write(detected_image)

        i+=1
    # df = pd.DataFrame(box_cnt_1)
    # df1 = pd.DataFrame(name_1)
    # df2 = pd.DataFrame(accuracy_1)
    # df3 = pd.DataFrame(boxbnd_1)
    # result = pd.DataFrame(results)    

    # df.to_csv(CNT_FILE_PATH)
    # df1.to_csv(CLASS_NAME_FILE_PATH)
    # df2.to_csv(ACCURACY_FILE_PATH)
    # df3.to_csv(BOXBND_FILE_PATH)
    # result.to_csv(RESULT_FILE_PATH)

    vid_writer.release()
    cap.release()
    lapse_time = round(time.time()-start, 5)
    print('### Video Detect 총 수행시간:', lapse_time)
    min = int(lapse_time / 60)
    second = ((lapse_time / 60) - min) * 60 
    print(f"총 수행시간은 {min}분 {second :.0f}초 걸렸습니다.")


    