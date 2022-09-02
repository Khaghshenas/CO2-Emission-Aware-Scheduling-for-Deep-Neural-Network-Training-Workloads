# CO2-Emission-Aware-Scheduling-for-Deep-Neural-Network-Training-Workloads

This repository includes the experiments data gathered by three commands:

1: nvidia-smi --query-gpu=index,timestamp,power.draw,clocks.sm,clocks.mem,clocks.gr,fan.speed,utilization.gpu,utilization.memory,temperature.gpu,pstate,memory.total,memory.free,memory.used --format=csv -l 5 -b![image](https://user-images.githubusercontent.com/39369208/188059708-a796b734-3b59-46cf-987e-9e44c8a9b9c1.png)
2: dstat --time --cpu --mem --load
3: top -u

The Data_logs folder 
