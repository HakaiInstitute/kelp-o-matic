# Model Performance

## Segmentation model performance by model name

All statistics are for the latest model revisions on the validation split of our internal training dataset. Please see
the [metric definitions](#metric-definitions) for mathematical definitions of each performance metric.

### *kelp-rgb*

#### Model Architecture

Two UNet++ EfficientNetV2-M, one for kelp presence/absence. One model is trained for kelp presence/absence detection,
and the other kelp species classification. Models are ensembled for final output using learned weights.

#### Performance
  | Class      |    IoU | Precision | Recall | F1     |
  |:-----------|-------:|----------:|-------:|-------:|
  | Macro      | 0.8816 |    0.9111 | 0.9645 | 0.9371 |
  | Nereo      | 0.8972 |    0.9484 | 0.9433 | 0.9458 |
  | Background | 0.9916 |    0.9964 | 0.9951 | 0.9958 |

### kelp-rgbi

#### Model Architecture

Two UNet++ EfficientNetB3 (SCSE decoder attention). One model is trained for kelp presence/absence detection, and the
other kelp species classification. Models are ensembled for final output using learned weights.

#### Performance
  | Class      |    IoU | Precision | Recall |     F1 |
  |:-----------|-------:|----------:|-------:|-------:|
  | Macro      | 0.9670 |    0.9787 | 0.9878 | 0.9832 |
  | Nereo      | 0.9328 |    0.9568 | 0.9738 | 0.9652 |
  | Background | 0.9988 |    0.9996 | 0.9992 | 0.9994 |

### kelp-ps8b

#### Model Architecture
SegFormer with mit-b3 feature extractor

#### Performance
  | Class |    IoU | Precision | Recall |     F1 |
  |:------|-------:|----------:|-------:|-------:|
  | Kelp  | 0.8901 |    0.9367 | 0.9472 | 0.9419 |

### mussel-rgb

#### Model Architecture
SegFormer with mit-b3 feature extractor

#### Performance
  | Class   |    IoU | Precision |   Recall |     F1 |
  |:--------|-------:|----------:|---------:|-------:|
  | Mussels | 0.8869 |    0.9343 |   0.9459 | 0.9401 |

### mussel-gooseneck-rgb

#### Model Architecture
SegFormer with mit-b3 feature extractor

#### Performance
  | Class        |    IoU | Precision | Recall |     F1 |
  |:-------------|-------:|----------:|-------:|-------:|
  | Mussels      | 0.8288 |    0.9119 | 0.9010 | 0.9064 |
  | Gooseneck B. | 0.7801 |    0.8652 | 0.8880 | 0.8765 |
  | Background   | 0.9831 |    0.9919 | 0.9911 | 0.9915 |

## Metric definitions

The following definitions describe the metrics used during training and evaluation of
the deep neural networks. They are important to understand for the sections following.

**Definitions in terms of pixel sets:**

- Let $A$ equal the set of human-labelled pixels.
- Let $B$ be defined as the set of pixel labels predicted by the model.
- Let $A_i$ and $B_i$ be the sets of pixels for a particular class of interest, $i$,
  from labels $A$ and $B$, respectively.

**Definitions in terms of true and false postive/negative classes:**

For class $i$:

- Let $TP_i$ be the true positives.
- Let $FP_i$ be the false positives.
- Let $TN_i$ be the true negatives.
- Let $FN_i$ be the false negatives.

**IoU**

:   The "intersection over union", also called the "Jaccard Index". Defined as:

$$
    IoU_i (A,B) = \frac{|A_i \cap B_i|}{|A_i \cup B_i|} = \frac{TP_i}{TP_i + FP_i + FN_i}
$$

**Precision**

:   The ratio of correct predictions for a class to the count of predictions of that
class:

$$
    Precision_i = \frac{|A_i \cap B_i|}{|A_i|} = \frac{TP_i}{TP_i + FP_i}
$$

**Recall**

:   The ratio of correct predictions for a class to the count of actual instances of
that class:

$$
    Recall_i = \frac{|A_i \cap B_i|}{|B_i|} = \frac{TP_i}{TP_i + FN_i}
$$

**F1**

:   The harmonic mean of precision and recall for a class, providing a single metric that balances both:

$$
    F1_i = 2 \cdot \frac{Precision_i \cdot Recall_i}{Precision_i + Recall_i} = \frac{2TP_i}{2TP_i + FP_i + FN_i}
$$
