# About

This document gives information about interpreting the Kelp-O-Matic model outputs, and gives 
details on the dataset pre-processing workflow, model training, and final performance achieved for 
both the kelp and mussel detection models.

## Model Outputs

Each of the Kelp-O-Matic models outputs a mask raster with integer pixel values that represent the
following classes:

### Kelp model output classes

| Output value | Class                        |
|-------------:|------------------------------|
|        **0** | Background                   |
|        **1** | Kelp *(presence mode)*       |
|        **2** | Macrocystis *(species mode)* |
|        **3** | Nereocystis *(species mode)* |

### Mussel model output classes

| Output value | Class      |
|-------------:|------------|
|        **0** | Background |
|        **1** | Mussles    |

## Dataset Preparation

The datasets used to train the kelp segmentation model were a number of scenes collected using DJI
Phantom remotely-piloted aircraft systems (RPAS). A total of 28 image mosaic scenes were used. The
resolution of each image varied between 0.023m and 0.428m, with an average of 0.069m and standard
deviation of 0.087m. These images were collected over a period from 2018 to 2021, all during summer.

For model training, each dataset was divided into 512 pixels square cropped sections, with 50%
overlap between adjacent tiles. To balance the dataset, tiles containing no kelp where discarded.
These sets of tiles where then divided into training, validation, and test splits.

Source code for data preparation is available on GitHub
at [:material-github: hakai-ml-dataprep](https://github.com/tayden/hakai-ml-dataprep).

#### Pre-processing overview

```mermaid
flowchart TD
    subgraph Data Preparation
    subgraph Labelling
    A[/"UAV Orthomosaic (RGB)"/] --> B[Manual kelp classification] 
    B --> C[/"Presence/Absence Dataset\n(not kelp = 0, kelp = 1)"/]
    B --> D[/"Species Dataset\n(not kelp = 0, Macrocystis = 2,\n Nereocystis = 3)"/]
    end
    subgraph Filtering [Prepare image tiles]
    E{{"Tile image and label\n(512x512 pixel tiles, 50% overlap)"}}
    E --> F{{"Discard image and labels tiles with no kelp\nOR where >50% is no data"}}
    end
    C & D--> Filtering
    subgraph PADataset [P/A Dataset]
    G[("Training ~80%")] 
    H[("Validation ~10%")]
    I[("Testing ~10%")]
    end
    subgraph SpeciesDataset [Species Dataset]
    G1[("Training ~80%")] 
    H1[("Validation ~10%")]
    I1[("Testing ~10%")]
    end
    Filtering --> PADataset & SpeciesDataset
    end
```

#### Dataset summaries

##### Kelp (presence/absence)
| Split    | # Scenes |  Tiles | Total pixels | Kelp pixels | Area (km^2^) | Res~max~ (m) | Res~min~ (m) | Res~$\mu$~ (m) | Res~$\sigma$~ (m) |
|:---------|---------:|-------:|-------------:|------------:|-------------:|-------------:|-------------:|---------------:|------------------:|
| Train    |       20 |  79410 |  20816855040 |  1869305638 |       962.39 |       0.1040 |       0.0230 |         0.0487 |            0.0253 |
| Val.     |        4 |  15805 |   4143185920 |   147658714 |       124.80 |       0.0420 |       0.0230 |         0.0296 |            0.0085 |
| Test     |        6 |  46304 |  12046802177 |   319847006 |       409.72 |       0.0680 |       0.0230 |         0.0385 |            0.0161 |
| $\Sigma$ |       30 | 141519 |  37006843137 |  2336811358 |      1496.92 |              |              |                |                   |

##### Kelp (species)

| Split    | # Scenes |  Tiles | Total pixels | Macro pixels | Nereo pixels |  Area (km^2^) | Res~max~ (m) | Res~min~ (m) | Res~$\mu$~ (m) | Res~$\sigma$~ (m) |
|:---------|---------:|-------:|-------------:|-------------:|-------------:|--------------:|-------------:|-------------:|---------------:|------------------:|
| Train    |       17 | 336740 |  88008624978 |    605462674 |   1158650042 | 4034113286.55 |       0.1040 |       0.0230 |         0.0488 |            0.0266 |
| Val.     |        4 |  15805 |   4110229732 |    127410722 |     20244320 |  123909899.85 |       0.0420 |       0.0230 |         0.0296 |            0.0085 |
| Test     |        6 |  46304 |  12046802177 |    143277498 |    176569508 |  409722875.67 |       0.0680 |       0.0230 |         0.0385 |            0.0161 |
| $\Sigma$ |       27 | 398849 | 104165656887 |    876150894 |   1355463870 |    4567746062 |              |              |                |                   |

##### Mussel (presence/absence)

!!! todo

    The mussel model is a work in progress. This section will be available in the future.

## Model Training

The LRASPP MobileNetV3-Large[^1] model was trained using a stochastic gradient descent optimizer
with the learning rate set to $0.35$, and L2 weight decay set to $3 \times 10^{-6}$. The model was
trained for a total of 100 epochs. A cosine annealing learning rate schedule[^2] was used to improve
accuracy. The loss function used for training was Focal Tversky Loss[^3], with parameters
$\alpha=0.7, \beta=0.3, \gamma=4.0 / 3.0$.

The model was trained on an AWS p3.8xlarge instance with 4 Nvidia Tesla V100 GPUS and took 18
hours to finish. At the end of training, the model parameters which achieved the best
IoU~$\mu$~ score on the validation data split were saved for inference. It is these parameters that 
were used to calculate the final performance statistics for the model on the test split.

Source code for model training is available on GitHub
at [:material-github: hakai-ml-train](https://github.com/tayden/hakai-ml-train).

[^1]: [A. Howard et al., ‘Searching for MobileNetV3’. arXiv, 2019.](https://arxiv.org/abs/1905.02244)
[^2]: [I. Loshchilov and F. Hutter, ‘SGDR: Stochastic Gradient Descent with Warm Restarts’. arXiv, 2016.](https://arxiv.org/abs/1608.03983)
[^3]: [N. Abraham and N. M. Khan, ‘A Novel Focal Tversky loss function with improved Attention U-Net for lesion segmentation’. arXiv, 2018.](https://arxiv.org/abs/1810.07842)

### Training overview

```mermaid
flowchart TD
    subgraph Training [CNN Training Loop]
    P(["Start"])
    P --> B2["Get next batch of training tiles"]
    G2[("Training")] -.-> B2
    subgraph Augmentation [Data Augmentation]
    J["Randomly rotation in [0, 45] deg"]
    J --> K["Random horizontal and/or vertical flip"]
    K --> L["Randomly jitter brightness,\ncontrast, and saturation"]
    end
    B2 --> Augmentation
    L --> Q["Forward pass through CNN"]
    Q --> R["Calculate error of CNN relative to hand-labelled images"]
    R --> S["Update CNN parameters with backpropagation"]
    S --> B3{"More training tiles\nto process?"}
    B3 -->|Yes| B2
    subgraph Validation
    H2[("Validation")] -.-> V["Calculate average model error on all batches"]
    end
    B3 -->|No| Validation
    Validation --> W{"Validation error is stabilized?\n(model converged)"}
    W --> |No| reset["Next training epoch"] --> B2
    W -->|Yes| X["Finished training,\nsave CNN model"]
    subgraph Testing
    I3[("Testing")] -.-> Y["Calculate model performance on all batches"]
    Y --> Z("Save model performance metrics") 
    end
    X --> Testing
    Testing --> End([End])
    end
```

## Model Performance

### Metric definitions

The following definitions describe the metrics used during training and evaluation of the deep
neural networks. They are important to understand for the sections following.

- Let $A$ equal the set of human-labelled pixels.

- Let $B$ be defined as the set of pixel labels predicted by the model.

- Let $A_i$ and $B_i$ be the sets of pixels for a particular class of interest, $i$, from labels $A$
  and $B$, respectively.

`Accuracy`

:   The ratio of counts of pixels correctly classified by the model divided over the total number of
pixels.


`IoU`

:   The "intersection over union", also called the "Jaccard Index". Defined as:

$$
IoU_i (A,B) = \frac{|A_i \cap B_i|}{|A_i \cup B_i|}
$$

`Mean IoU (mIoU)`

:   The mean of the intersection over union values over all classes. Defined as:

$$
mIoU (A,B) = \frac{\sum_{i=1}^{c} IoU_{i}(A,B)}{c}
$$

### Summary statistics

#### Kelp (presence/absence)

##### Validation split

| IoU~bg~ | IoU~kelp~ | IoU~$\mu$~ | Accuracy |
|---------|-----------|------------|----------|
| 0.9857  | 0.6964    | 0.8410     | 0.9865   |

##### Test split

| IoU~bg~ | IoU~kelp~ | IoU~$\mu$~ | Accuracy |
|---------|-----------|------------|----------|
| 0.9884  | 0.6541    | 0.8213     | 0.9890   |

#### Kelp (species)

##### Validation split

| IoU~bg~ | IoU~macro~ | IoU~nereo~ | mIoU   | Accuracy |
|---------|------------|------------|--------|----------|
| 0.9423  | 0.7392     | 0.4369     | 0.7810 | 0.9522   |

##### Test split

| IoU~bg~ | IoU~macro~ | IoU~nereo~ | mIoU   | Accuracy |
|---------|------------|------------|--------|----------|
| 0.9883  | 0.7574     | 0.5262     | 0.7607 | 0.9880   |

#### Mussel (presence/absence)

!!! todo

    The mussel model is a work in progress. This section will be updated in the future.

##### Validation split

| IoU~bg~ | IoU~mussels~ | mIoU   | Accuracy |
|---------|--------------|--------|----------|
| 0.9622  | 0.7188       | 0.8405 | 0.9678   |
