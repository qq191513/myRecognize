# -*- encoding: utf8 -*-
# author: ronniecao
import sys
import os
import numpy
import matplotlib.pyplot as plt
import tensorflow as tf
from src.layer.conv_layer import ConvLayer
from src.layer.dense_layer import DenseLayer
from src.layer.pool_layer import PoolLayer
import numpy as np
from src.model.squeezenet import squeezenet
from src.model.squeezenet import squeezenet_arg_scope
slim = tf.contrib.slim
trunc_normal = lambda stddev: tf.truncated_normal_initializer(0.0, stddev)
import time
min_depth =16
depth_multiplier=1.0
concat_dim = 3
depth = lambda d: max(int(d * depth_multiplier), min_depth)
#Numpy花式索引，获取所有元素的出现次数
def all_np(arr):
    arr = np.array(arr)
    key = np.unique(arr)
    result = {}
    for k in key:
        mask = (arr == k)
        arr_new = arr[mask]
        v = arr_new.size
        result[k] = v
    return result


def find_dict_max_key(result = {}):
    max_value = 0
    max_key = 0
    for key in result.keys():
        if result[key] > max_value:
            max_value = result[key]
            max_key = key
    return max_key

def print_and_save_txt(str=None,filename=r'log.txt'):
    with open(filename, "a+") as log_writter:
        print(str)
        log_writter.write(str)



class ConvNet():
    def __init__(self, n_channel=3, n_classes=10, image_size=24, n_layers=44):
        # 设置超参数
        self.n_channel = n_channel
        self.n_classes = n_classes
        self.image_size = image_size
        self.n_layers = n_layers

        # 输入变量
        self.images = tf.placeholder(
            dtype=tf.float32, shape=[None, self.image_size, self.image_size, self.n_channel],
            name='images')
        self.labels = tf.placeholder(
            dtype=tf.int64, shape=[None], name='labels')
        self.keep_prob = tf.placeholder(
            dtype=tf.float32, name='keep_prob')
        self.global_step = tf.Variable(
            0, dtype=tf.int32, name='global_step')

        # 网络输出
        conv_layer1 = ConvLayer(
            input_shape=(None, image_size, image_size, n_channel), n_size=3, n_filter=3,
            stride=1,activation='relu', batch_normal=True, weight_decay=1e-4,
            name='conv1')

        # 数据流
        basic_conv = conv_layer1.get_output(input=self.images)


        # basic_conv = conv_layer1.get_output(input=self.images)
        # with slim.arg_scope(squeezenet_arg_scope()):
        hidden_conv, dense_layer1= self.residual_googlev2_inference(images=basic_conv, scope_name='net_1')
        self.logits_1 = self.son_google_v2_part(hidden_conv, dense_layer1)



        # 目标函数
        self.objective_1 = tf.reduce_sum(
            tf.nn.sparse_softmax_cross_entropy_with_logits(
                logits=self.logits_1, labels=self.labels))




        self.objective = self.objective_1


        tf.add_to_collection('losses', self.objective)
        self.avg_loss = tf.add_n(tf.get_collection('losses'))

        # 优化器
        lr = tf.cond(tf.less(self.global_step, 50000),
                     lambda: tf.constant(0.01),
                     lambda: tf.cond(tf.less(self.global_step, 100000),
                                     lambda: tf.constant(0.005),
                                     lambda: tf.cond(tf.less(self.global_step, 150000),
                                                     lambda: tf.constant(0.001),
                                                     lambda: tf.constant(0.001))))
        self.optimizer = tf.train.AdamOptimizer(learning_rate=lr).minimize(
            self.avg_loss, global_step=self.global_step)

        # 观察值
        correct_prediction_1 = tf.equal(self.labels, tf.argmax(self.logits_1, 1))
        self.accuracy_1 = tf.reduce_mean(tf.cast(correct_prediction_1, 'float'))

    def son_google_v2_part(self,hidden_conv,dense_layer1):
        # google_v2_part
        with tf.variable_scope('InceptionV2'):
            with slim.arg_scope(
                    [slim.conv2d, slim.max_pool2d, slim.avg_pool2d],
                    stride=1,
                    padding='SAME'):
                with tf.variable_scope('Branch_0'):
                    branch_0 = slim.conv2d(hidden_conv, depth(352), [1, 1], scope='Conv2d_0a_1x1')
                with tf.variable_scope('Branch_1'):
                    branch_1 = slim.conv2d(
                        hidden_conv, depth(192), [1, 1],
                        weights_initializer=trunc_normal(0.09),
                        scope='Conv2d_0a_1x1')
                    branch_1 = slim.conv2d(branch_1, depth(320), [3, 3],
                                           scope='Conv2d_0b_3x3')
                with tf.variable_scope('Branch_2'):
                    branch_2 = slim.conv2d(
                        hidden_conv, depth(160), [1, 1],
                        weights_initializer=trunc_normal(0.09),
                        scope='Conv2d_0a_1x1')
                    branch_2 = slim.conv2d(branch_2, depth(224), [3, 3],
                                           scope='Conv2d_0b_3x3')
                    branch_2 = slim.conv2d(branch_2, depth(224), [3, 3],
                                           scope='Conv2d_0c_3x3')
                with tf.variable_scope('Branch_3'):
                    branch_3 = slim.avg_pool2d(hidden_conv, [2, 2], scope='AvgPool_0a_3x3')
                    branch_3 = slim.conv2d(
                        branch_3, depth(128), [1, 1],
                        weights_initializer=trunc_normal(0.1),
                        scope='Conv2d_0b_1x1')
                hidden_conv = tf.concat(
                    axis=concat_dim, values=[branch_0, branch_1, branch_2, branch_3])

        # global average pooling
        input_dense1 = tf.reduce_mean(hidden_conv, reduction_indices=[1, 2])
        logits = dense_layer1.get_output(input=input_dense1)
        return logits

    def residual_googlev2_inference(self, images,scope_name):
        with tf.variable_scope(scope_name):
            n_layers = int((self.n_layers - 2) / 6)
            # 网络结构
            conv_layer0_list = []
            conv_layer0_list.append(
                ConvLayer(
                    input_shape=(None, self.image_size, self.image_size, 3),
                    n_size=3, n_filter=64, stride=1, activation='relu',
                    batch_normal=True, weight_decay=1e-4, name='conv0'))

            conv_layer1_list = []
            for i in range(1, n_layers+1):
                conv_layer1_list.append(
                    ConvLayer(
                        input_shape=(None, self.image_size, self.image_size, 64),
                        n_size=3, n_filter=64, stride=1, activation='relu',
                        batch_normal=True, weight_decay=1e-4, name='conv1_%d' % (2*i-1)))
                conv_layer1_list.append(
                    ConvLayer(
                        input_shape=(None, self.image_size, self.image_size, 64),
                        n_size=3, n_filter=64, stride=1, activation='none',
                        batch_normal=True, weight_decay=1e-4, name='conv1_%d' % (2*i)))

            conv_layer2_list = []
            conv_layer2_list.append(
                ConvLayer(
                    input_shape=(None, self.image_size, self.image_size, 64),
                    n_size=3, n_filter=128, stride=2, activation='relu',
                    batch_normal=True, weight_decay=1e-4, name='conv2_1'))
            conv_layer2_list.append(
                ConvLayer(
                    input_shape=(None, int(self.image_size)/2, int(self.image_size)/2, 128),
                    n_size=3, n_filter=128, stride=1, activation='none',
                    batch_normal=True, weight_decay=1e-4, name='conv2_2'))
            for i in range(2, n_layers+1):
                conv_layer2_list.append(
                    ConvLayer(
                        input_shape=(None, int(self.image_size/2), int(self.image_size/2), 128),
                        n_size=3, n_filter=128, stride=1, activation='relu',
                        batch_normal=True, weight_decay=1e-4, name='conv2_%d' % (2*i-1)))
                conv_layer2_list.append(
                    ConvLayer(
                        input_shape=(None, int(self.image_size/2), int(self.image_size/2), 128),
                        n_size=3, n_filter=128, stride=1, activation='none',
                        batch_normal=True, weight_decay=1e-4, name='conv2_%d' % (2*i)))

            conv_layer3_list = []
            conv_layer3_list.append(
                ConvLayer(
                    input_shape=(None, int(self.image_size/2), int(self.image_size/2), 128),
                    n_size=3, n_filter=256, stride=2, activation='relu',
                    batch_normal=True, weight_decay=1e-4, name='conv3_1'))
            conv_layer3_list.append(
                ConvLayer(
                    input_shape=(None, int(self.image_size/4), int(self.image_size/4), 256),
                    n_size=3, n_filter=256, stride=1, activation='relu',
                    batch_normal=True, weight_decay=1e-4, name='conv3_2'))
            for i in range(2, n_layers+1):
                conv_layer3_list.append(
                    ConvLayer(
                        input_shape=(None, int(self.image_size/4), int(self.image_size/4), 256),
                        n_size=3, n_filter=256, stride=1, activation='relu',
                        batch_normal=True, weight_decay=1e-4, name='conv3_%d' % (2*i-1)))
                conv_layer3_list.append(
                    ConvLayer(
                        input_shape=(None, int(self.image_size/4), int(self.image_size/4), 256),
                        n_size=3, n_filter=256, stride=1, activation='none',
                        batch_normal=True, weight_decay=1e-4, name='conv3_%d' % (2*i)))

            dense_layer1 = DenseLayer(
                input_shape=(None, 1024),
                hidden_dim=self.n_classes,
                activation='none', dropout=False, keep_prob=None,
                batch_normal=False, weight_decay=1e-4, name='dense1')

            # 数据流
            hidden_conv = conv_layer0_list[0].get_output(input=images)

            for i in range(0, n_layers):
                hidden_conv1 = conv_layer1_list[2*i].get_output(input=hidden_conv)
                hidden_conv2 = conv_layer1_list[2*i+1].get_output(input=hidden_conv1)
                hidden_conv = tf.nn.relu(hidden_conv + hidden_conv2)

            hidden_conv1 = conv_layer2_list[0].get_output(input=hidden_conv)
            hidden_conv2 = conv_layer2_list[1].get_output(input=hidden_conv1)
            hidden_pool = tf.nn.max_pool(
                hidden_conv, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
            hidden_pad = tf.pad(hidden_pool, [[0,0], [0,0], [0,0], [32,32]])
            hidden_conv = tf.nn.relu(hidden_pad + hidden_conv2)
            for i in range(1, n_layers):
                hidden_conv1 = conv_layer2_list[2*i].get_output(input=hidden_conv)
                hidden_conv2 = conv_layer2_list[2*i+1].get_output(input=hidden_conv1)
                hidden_conv = tf.nn.relu(hidden_conv + hidden_conv2)

            hidden_conv1 = conv_layer3_list[0].get_output(input=hidden_conv)
            hidden_conv2 = conv_layer3_list[1].get_output(input=hidden_conv1)
            hidden_pool = tf.nn.max_pool(
                hidden_conv, ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME')
            hidden_pad = tf.pad(hidden_pool, [[0,0], [0,0], [0,0], [64,64]])
            hidden_conv = tf.nn.relu(hidden_pad + hidden_conv2)
            for i in range(1, n_layers):
                hidden_conv1 = conv_layer3_list[2*i].get_output(input=hidden_conv)
                hidden_conv2 = conv_layer3_list[2*i+1].get_output(input=hidden_conv1)
                hidden_conv = tf.nn.relu(hidden_conv + hidden_conv2)


            return hidden_conv,dense_layer1

    def get_1_acc_list(self, test_images, test_labels, n_test, batch_size, is_train=True):
        # 计算准确率
        accuracy_1_list = []
        batchs_number = 0
        for i in range(0, n_test, batch_size):
            batch_images = test_images[i: i + batch_size]
            batch_labels = test_labels[i: i + batch_size]

            [avg_accuracy_1] = self.sess.run(
                fetches=[self.accuracy_1],
                feed_dict={self.images: batch_images,
                           self.labels: batch_labels,
                           self.keep_prob: 1.0})

            accuracy_1_list.append(avg_accuracy_1)
            batchs_number += 1

            if not is_train:
                print('batches: {} , avg_accuracy_1: {}'.format(batchs_number, avg_accuracy_1))

        return accuracy_1_list
        
    def train(self, dataloader, backup_path, n_epoch=5, batch_size=128):
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        # 构建会话
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
        self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        # 模型保存器
        self.saver = tf.train.Saver(
            var_list=tf.global_variables(), write_version=tf.train.SaverDef.V2, 
            max_to_keep=5)

        # 模型初始化
        # self.sess.run(tf.global_variables_initializer())
        try:
            print("\nTrying to restore last checkpoint ...")
            last_chk_path = tf.train.latest_checkpoint(checkpoint_dir=backup_path)
            self.saver.restore(self.sess, save_path=last_chk_path)
            print("Restored checkpoint from:", last_chk_path)
        except ValueError:
            print("\nFailed to restore checkpoint. Initializing variables instead.")
            self.sess.run(tf.global_variables_initializer())
        
        # 验证集数据增强
        valid_images = dataloader.data_augmentation(dataloader.valid_images, mode='test',
            flip=False, crop=True, crop_shape=(24,24,3), whiten=True, noise=False)
        valid_labels = dataloader.valid_labels
        # 模型训练
        since = time.time()

        start_n_epoch = 0
        for epoch in range(start_n_epoch, n_epoch + 1):

            # 训练集数据增强
            train_images = dataloader.data_augmentation(dataloader.train_images, mode='train',
                                                        flip=True, crop=True, crop_shape=(24, 24, 3), whiten=True,
                                                        noise=False)
            train_labels = dataloader.train_labels

            # 开始本轮的训练，并计算目标函数值
            train_loss = 0.0
            get_global_step = 0
            for i in range(0, dataloader.n_train, batch_size):
                # for i in range(0, 300, batch_size):
                batch_images = train_images[i: i + batch_size]
                batch_labels = train_labels[i: i + batch_size]
                [_, avg_loss, get_global_step] = self.sess.run(
                    fetches=[self.optimizer, self.avg_loss, self.global_step],
                    feed_dict={self.images: batch_images,
                               self.labels: batch_labels,
                               self.keep_prob: 0.5})
                if get_global_step % 20 == 0:
                    print('global_step: {} ,data_batch idx: {} , batch_loss: {}'.format(get_global_step, i, avg_loss))
                train_loss += avg_loss * batch_images.shape[0]
            train_loss = 1.0 * train_loss / dataloader.n_train

            # 获取验证准确率列表
            if epoch % 5 == 0:
                accuracy_1_list = \
                    self.get_1_acc_list(valid_images, valid_labels, dataloader.n_valid, batch_size, True)

                message_1 = 'epoch: {} , global_step: {}\n'.format(epoch, get_global_step)
                message_2 = 'net1: %.4f\n' % (np.mean(accuracy_1_list))

                print_and_save_txt(str=message_1 + message_2,
                                   filename=os.path.join(backup_path, 'train_log.txt'))

            # 保存模型
            if epoch % 10 == 0:
                print('saving model.....')
                saver_path = self.saver.save(
                    self.sess, os.path.join(backup_path, 'model_%d.ckpt' % (epoch)))

        time_elapsed = time.time() - since
        seconds = time_elapsed % 60
        hours = time_elapsed // 3600
        mins = (time_elapsed - hours * 3600) / 3600 * 60
        time_message = 'The code run {:.0f}h {:.0f}m {:.0f}s\n'.format(
            hours, mins, seconds)
        print_and_save_txt(str=time_message, filename=os.path.join(backup_path, 'train_log.txt'))

        self.sess.close()
                
    def test(self, dataloader, backup_path, epoch, batch_size=128):
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.8)
        self.sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
        # 读取模型
        self.saver = tf.train.Saver(write_version=tf.train.SaverDef.V2)
        model_path = os.path.join(backup_path, 'model_%d.ckpt' % (epoch))
        assert(os.path.exists(model_path+'.index'))
        self.saver.restore(self.sess, model_path)
        print('read model from %s' % (model_path))


        test_images = dataloader.data_augmentation(dataloader.test_images,
                                                   flip=False, crop=True, crop_shape=(24, 24, 3), whiten=True,
                                                   noise=False)
        test_labels = dataloader.test_labels

        # 获取全部准确率列表
        accuracy_1_list = self.get_1_acc_list(test_images, test_labels, dataloader.n_test, batch_size, is_train=False)

        message_1 = 'test result: \n'
        message_2 = 'net1: %.4f\n' % (np.mean(accuracy_1_list))

        print_and_save_txt(str=message_1 + message_2,
                           filename=os.path.join(backup_path, 'test_log.txt'))

        #########  parameters numbers###########
        from functools import reduce
        from operator import mul
        def get_num_params():
            num_params = 0
            for variable in tf.trainable_variables():
                shape = variable.get_shape()
                num_params += reduce(mul, [dim.value for dim in shape], 1)
            return num_params

        print_and_save_txt(str='xxxxxxxxxxxxxx parament numbers is : %d xxxxxxxxxxxxxxx' % get_num_params(),
                           filename=os.path.join(backup_path, 'test_log.txt'))
        #######################################

        self.sess.close()
            
    def debug(self):
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        [temp] = sess.run(
            fetches=[self.logits],
            feed_dict={self.images: numpy.random.random(size=[128, 24, 24, 3]),
                       self.labels: numpy.random.randint(low=0, high=9, size=[128,]),
                       self.keep_prob: 1.0})
        print(temp.shape)