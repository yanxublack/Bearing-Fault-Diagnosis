#Tensorflow中用tfrecords制作二进制文件用于一维数据段和标签的加载，读取时可提高内存利用率
#coding: utf-8
import tensorflow as tf
import numpy as np
from PIL import Image
import os

segments_train_path = "C:\\Users\\Administrator\\PycharmProjects\\DA_testmodel\\train_dataset\\"
label_train_path = "C:\\Users\\Administrator\\PycharmProjects\\DA_testmodel\\ead_train.txt"
tfRecord_train = './data/segment_train.tfrecords'
segments_test_path = "C:\\Users\\Administrator\\PycharmProjects\\DA_testmodel\\test_dataset\\"
label_test_path = "C:\\Users\\Administrator\\PycharmProjects\\DA_testmodel\\ead_test.txt"
tfRecord_test = './data/segment_test.tfrecords'
data_path = "./data"


def generate_tfRecord():
    isExists = os.path.exists(data_path)
    if not isExists:
        os.makedirs(data_path)
        print("The directory was created successfully!")
    else:
        print("directory already exists!")
    write_tfRecord(tfRecord_train, segments_train_path, label_train_path)
    write_tfRecord(tfRecord_test, segments_test_path, label_test_path)

#制作tfRecord数据集以便后续应用
def write_tfRecord(tfRecordName, image_path, label_path):
    writer = tf.io.TFRecordWriter(tfRecordName)
    num_segment = 0 #计数器，用于显示进度
    f = open(label_path,'r')
    contents = f.readlines()
    f.close()
    for content in contents:
        value = content.split()
        img_path = image_path + value[0]
        segment = np.load(img_path)
        segment_raw = segment.tobytes()
        labels = [0] * 4
        labels[int(value[1])] = 1  #one-hot编码

        example = tf.train.Example(features=tf.train.Features(feature={'img_raw':tf.train.Feature(bytes_list=tf.train.BytesList(value=[segment_raw])),
                                                                       'label':tf.train.Feature(int64_list=tf.train.Int64List(value=labels))}))
        writer.write(example.SerializeToString())
        num_segment += 1
        print("the number of picture:",num_segment)
    writer.close()
    print("write tfrecord successfully!")

#批量读取tfRecord数据集
#定义解码格式
feature_description = {
    'label':tf.io.FixedLenFeature([4],tf.int64),
    'img_raw':tf.io.FixedLenFeature([],tf.string)
}
def _parse_image_function(example_proto):
  # Parse the input `tf.Example` proto using the dictionary above.
  return tf.io.parse_single_example(example_proto, feature_description)

def read_tfRecord(tfRecord_path):
    img_data = []
    label_data = []
    filename_queue = tf.data.Dataset.from_tensor_slices([tfRecord_path])
    serialized_example = tf.data.TFRecordDataset(filename_queue)
    parsed_image_dataset = serialized_example.map(_parse_image_function)
    for imgs in parsed_image_dataset:
        img = tf.io.decode_raw(imgs['img_raw'], tf.float64)  # 解码序列化数据
        #img.set_shape([4096])  # 64 * 64
        #img = tf.cast(img, tf.float32) * (1. / 255)  # 像素值归一化
        label = tf.cast(imgs['label'], tf.float32)
        img_data.append(img)
        label_data.append(label)
    img_data = np.asarray(img_data)
    label_data = np.asarray(label_data)
    return img_data, label_data

def get_tfrecord():  #批量化读取
    train_images, train_labels = read_tfRecord(tfRecord_train)
    validation_images, validation_labels = read_tfRecord(tfRecord_test)
    return train_images, train_labels, validation_images, validation_labels

def main():
    generate_tfRecord()

if __name__ == '__main__':
    main()