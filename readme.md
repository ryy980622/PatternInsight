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

The prepocessed sequential data of Dataset Vehicle and Sensor can be downloaded from [here](https://drive.google.com/drive/folders/1kdqxAH30vOAQlq2-3J3JEU2QObVxKn5r?usp=sharing).

The prepocessed pattern data of Dataset Vehicle and Sensor is placed in ./data.
## Running

First, construct the multi-level aggregation plan by running

```
python CASEM.py 
```

Then, evaluate the performances of PatternInsight on Vehicle dataset by running

```
python online_detection_traffic.py 
```

The similar process can be applied to the Sensor dataset by running

```
python online_detection_pollution.py 
```