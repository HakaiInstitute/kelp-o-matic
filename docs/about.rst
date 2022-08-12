About
=====

This document details the datasets used to produce the contained tools and documents the current performance statistics achieved
during model training.

Metric definitions
------------------

The following definitions describe the metrics used during training and evaluation of the deep neural networks. They are
important to understand for the sections following.

- Let :math:`A` equal the set of human-labelled pixels.

- Let :math:`B` be defined as the set of pixel labels predicted by the model.

- Let :math:`A_i` and :math:`B_i` be the sets of pixels for a particular class of interest, :math:`i`, from labels :math:`A` and :math:`B`, respectively.

Accuracy
    The ratio of counts of pixels correctly classified by the model divided over the total number of pixels.


IoU
    The "intersection over union", also called the "Jaccard Index". Defined as:

    .. math::

        IoU_i (A,B) = \frac{|A_i \cap B_i|}{|A_i \cup B_i|}

Mean IoU
    The mean of the intersection over union values over all classes. Defined as:

    .. math::

        mIoU (A,B) = \frac{\sum_{i=1}^{c} IoU_{i}(A,B)}{c}

-------------------------------------------------------------------------------------------------------------------------------

find-kelp
---------

Output classes
..............

- 0 = background
- 1 = kelp
- 2 = macrocystis (when using species mode only)
- 3 = nereocystis (when using species mode only)

Dataset
.......

The datasets used to train the kelp segmentation model were a number of scenes collected using DJI Phantom remotely-piloted
aircraft systems (RPAS). A total of 28 image mosaic scenes were used. The resolution of each image varied between
0.023m and 0.428m, with an average of 0.069m and standard deviation of 0.087m. These images were collected over a period from
2018 to 2021, all during the summer season.

For model training, each dataset was divided into 512 pixels square cropped sections, with 50% overlap between adjacent tiles.
To balance the dataset, tiles containing no kelp where discarded. These sets of tiles where then divided into training,
validation, and test splits with the following summary statistics:

.. TODO: Details about ground area covered

=====   ===========   ============   ===========   ==============   ===============   =============   ===============
Split   Tiles         Total pixels   Kelp pixels   Max. res. (m)    Min res. (m)      Avg. res. (m)   Stdev. res. (m)
=====   ===========   ============   ===========   ==============   ===============   =============   ===============
Train   54233         14216855552    1869302818    0.023            0.428             0.072           0.090
Val     3667          961282048      147658714     0.023            0.272             0.091           0.121
Test    4019          1053556736     156686376     0.023            0.068             0.040           0.020
=====   ===========   ============   ===========   ==============   ===============   =============   ===============


.. TODO: Details about mussels dataset


Training configuration
......................

.. _find-kelp Training Configuration:

The `LRASPP MobileNetV3-Large <https://arxiv.org/abs/1905.02244>`_ model was trained using a stochastic gradient descent optimizer
with the learning rate set to :math:`0.35`, and L2 weight decay set to :math:`3 \times 10^{-6}`. The model was trained for a total
of 100 epochs. A `cosine annealing learning rate schedule <https://arxiv.org/abs/1608.03983>`_ was used to improve accuracy.
The loss function used for training was `Focal Tversky Loss <https://arxiv.org/abs/1608.03983>`_, with parameters :math:`\alpha=0.7, \beta=0.3, \gamma=4.0 / 3.0`.

The model was trained on an AWS "p3.8xlarge" instance with 4 Nvidia Tesla V100 GPUS and took 18 hours and 1 minute to finish.
At the end of training, the model parameters which achieved the best mIoU score on the validation data split were saved for inference.
These parameters were used to calculate the final performance statistics for the model (see `Kelp Model Performance`_).

Full source code for training the kelp model is available at https://github.com/tayden/hakai-ml-train.

Performance
...........

.. _Kelp Model Performance:

Presence/Absence Model
^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Validation split results
    :widths: 25 25 25 25
    :header-rows: 1

    * - IoU :sub:`bg`
      - IoU :sub:`kelp`
      - mIoU
      - Accuracy
    * - 0.9437
      - 0.6609
      - 0.8023
      - 0.9555

.. list-table:: Test split results
    :widths: 25 25 25 25
    :header-rows: 1

    * - IoU :sub:`bg`
      - IoU :sub:`kelp`
      - mIoU
      - Accuracy
    * - 0.9286
      - 0.5930
      - 0.76077
      - 0.93844

Species Model
^^^^^^^^^^^^^

.. list-table:: Validation split results
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - IoU :sub:`bg`
      - IoU :sub:`macro`
      - IoU :sub:`nereo`
      - mIoU
      - Accuracy
    * - 0
      - 0
      - 0
      - 0
      - 0

.. list-table:: Test split results
    :widths: 25 25 25 25 25
    :header-rows: 1

    * - IoU :sub:`bg`
      - IoU :sub:`macro`
      - IoU :sub:`nereo`
      - mIoU
      - Accuracy
    * - 0
      - 0
      - 0
      - 0
      - 0

-------------------------------------------------------------------------------------------------------------------------------

find-mussels
------------

Output classes
..............

- 0 = background
- 1 = mussels

Dataset
.......

*TODO*

Training configuration
......................

The `LRASPP MobileNetV3-Large <https://arxiv.org/abs/1905.02244>`_ model used for mussel detection was trained using identical
hyperparameters as the Kelp Model. See the `find-kelp Training Configuration`_ for details.

The full source code for training the mussel detection model is also available at https://github.com/tayden/hakai-ml-train.

Performance
...........

.. _Mussel Model Performance:

.. list-table:: Validation split results
    :widths: 25 25 25 25
    :header-rows: 1

    * - IoU :sub:`bg`
      - IoU :sub:`mussels`
      - mIoU
      - Accuracy
    * - 0.9622
      - 0.7188
      - 0.8405
      - 0.9678
