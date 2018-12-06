# TransE
A TensorFlow implementation of TransE model in [Translating Embeddings for Modeling
Multi-relational Data](https://www.utc.fr/~bordesan/dokuwiki/_media/en/transe_nips13.pdf)

## Setup

1. Checkout project via git
2. [Install Anaconda](http://docs.continuum.io/anaconda/install) 
3. Create a new conda environment using anaconda

    ```conda create --name TransE python=3.6``` 

4. Activate your the environment

    ```source activate TransE```

5. Use pip to install all dependencies from the requirements txt

    ```pip install -r requirements.txt```


# Performance
| Datasets | MeanRank(Raw) | MeanRank(Filter) | Hits@10(Raw)(%) | Hits@10(Filter)(%) | Epochs |
| :------: | :-----------: | :--------------: | :-------------: | :----------------: | :----: |
| WN18 | 243 | 231 | 79.9 | 93.9 | 1000 |
| FB15k | 246 | 92 | 47.7 | 74.0 | 2000 |

Download the datasets(WN18 and FB15k) from [this repo](https://github.com/thunlp/KB2E).
