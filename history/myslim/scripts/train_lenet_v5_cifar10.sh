#!/bin/bash

set -e

###############dataset1
TRAIN_DIR=log/lenet/v5_cifar10_process_cifarnet
MODEL_NAME=lenet_v5
DATASET_DIR=datasets/cifar-10
DATASET_NAME=cifar10
PREPROCESSING_NAME=cifarnet
################################


# Run training.
python train_image_classifier_MIMO.py \
  --train_dir=${TRAIN_DIR} \
  --dataset_name=${DATASET_NAME} \
  --dataset_split_name=train \
  --dataset_dir=${DATASET_DIR} \
  --model_name=${MODEL_NAME} \
  --preprocessing_name=${PREPROCESSING_NAME} \
  --save_interval_secs=300 \
  --max_number_of_steps=40000 \
  --batch_size=50 \
  --learning_rate=0.001 \
  --save_summaries_secs=60 \
  --log_every_n_steps=100 \
  --optimizer=adam \
  --learning_rate_decay_type=exponential \
  --weight_decay=0.00004


# Run evaluation.
python eval_image_classifier_MIMO.py \
  --batch_size=100 \
  --checkpoint_path=${TRAIN_DIR} \
  --preprocessing_name=${PREPROCESSING_NAME} \
  --eval_dir=${TRAIN_DIR} \
  --dataset_name=${DATASET_NAME} \
  --dataset_split_name=test \
  --dataset_dir=${DATASET_DIR} \
  --model_name=${MODEL_NAME}
