# CO2-Emission-Aware-Scheduling-for-Deep-Neural-Network-Training-Workloads

This repository contains the experiments data of the paper "CO2-Emission-Aware-Scheduling-for-Deep-Neural-Network-Training-Workloads".

##Directory Structure
###Data_logs

This folder includes the outputs of the experiments gathered by three commands:

1: nvidia-smi --query-gpu=index,timestamp,power.draw,clocks.sm,clocks.mem,clocks.gr,fan.speed,utilization.gpu,utilization.memory,temperature.gpu,pstate,memory.total,memory.free,memory.used --format=csv -l 5 -b

2: dstat --time --cpu --mem --load

3: top -u

The output folder contains the data for training Alexnet, APS, LSTM, NAS, Resnet-18, Transformer_base,Vgg-16, and Wavenet models for a few epochs. The output_multi_jobs contains the data for running APS and LSTM models on the same set of GPUs. The outputs_n_GPUs contains the data for training Vgg-16 on different number of GPUs with different batch sizes. 


The data is loaded and processed by notebooks
