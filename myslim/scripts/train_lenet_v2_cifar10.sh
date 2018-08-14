#!/bin/bash

set -e

###############dataset1
TRAIN_DIR=log/lenet/v2_cifar10_process_cifarnet
DATASET_DIR=datasets/cifar-10
DATASET_NAME=cifar10
MODEL_NAME=lenet_v2
PREPROCESSING_NAME=cifarnet
################################


# Run training.
python train_image_classifier.py \
  --train_dir=${TRAIN_DIR} \
  --dataset_name=${DATASET_NAME} \
  --dataset_split_name=train \
  --dataset_dir=${DATASET_DIR} \
  --model_name=${MODEL_NAME} \
  --preprocessing_name=${PREPROCESSING_NAME} \
  --save_interval_secs=300 \
  --max_number_of_steps=80000 \
  --batch_size=50 \
  --learning_rate=0.001 \
  --save_summaries_secs=60 \
  --log_every_n_steps=50 \
  --optimizer=adam \
  --learning_rate_decay_type=exponential \
  --weight_decay=0.00004


# Run evaluation.
python eval_image_classifier.py \
  --batch_size=100 \
  --checkpoint_path=${TRAIN_DIR} \
  --preprocessing_name=${PREPROCESSING_NAME} \
  --eval_dir=${TRAIN_DIR} \
  --dataset_name=${DATASET_NAME} \
  --dataset_split_name=test \
  --dataset_dir=${DATASET_DIR} \
  --model_name=${MODEL_NAME}
