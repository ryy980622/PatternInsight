# PatternInsight: An Online Approach to Complex Pattern Detection over Mobile Data Streams

This repository contains the replication of the paper **"PatternInsight: An Online Approach to Complex
Pattern Detection over Mobile Data Streams"**.

## Overview
This paper explores how to significantly accelerate aggregation so as to make pattern detection online executable.
By comprehensively investigating a wide variety of mobile data streams, the authors note the existence of a latent hierarchical cluster structure
among complex patterns (in terms of their instance similarities), which can be utilized to quickly aggregate common instances without
going through the exponential solution space. To extract the latent information, the authors devise a content-aware structural entropy minimization
algorithm to properly determine intra-cluster patterns, together with a lightweight differential compensation mechanism to maintain those
inter-cluster “residual” relations among patterns.
## Dataset

The prepocessed streaming data of Dataset Vehicle and Sensor can be downloaded from [here](https://drive.google.com/drive/folders/1kdqxAH30vOAQlq2-3J3JEU2QObVxKn5r?usp=sharing).

The prepocessed complex patterns of Dataset Vehicle and Sensor are placed in ./data. 
## Baselines
To construct the tree using RW baseline, please run

```
python RW.py 
```

and 

```
python RW_tree.py 
```

To construct the tree using SPASS baseline, please run

```
python SPASS.py 
```

## CASEM

To construct the tree using the proposed CASEM algorithm, please run

```
python CASEM.py 
```

To further implement the CASEM+DCE algorithm, please run

```
python CASEM+DCE.py 
```

## Evaluation

For all the methods, evaluate the performances on Vehicle dataset by running

```
python online_detection_traffic.py 
```

The similar process can be applied to the Sensor dataset by running

```
python online_detection_pollution.py 
```