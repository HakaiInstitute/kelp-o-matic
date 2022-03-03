About
=====

.. TODO: Overview
.. TODO: ~~~~~~~~

Datasets
--------

The datasets used to train the models are a number of scenes collected using DJI Phantom remotely-piloted aircraft systems (RPAS).

Kelp
....

For the kelp model, a total of 28 image mosaic scenes were used. The resolution of each image varied between
0.023m and 0.428m, with an average of 0.069m and standard deviation of 0.087m. These images were collected over a period from
2018 to 2021, all during the summer season. For model training, each dataset was divided into 512 pixels square cropped sections,
with 50% overlap between adjacent tiles. To balance the dataset, tiles containing no kelp where discarded. These sets of tiles
where then divided into training, validation, and test splits with the following summary statistics:

.. TODO: Details about ground area covered

=====   ===========   ============   ===========   ==============   ===============   =============   ===============
Split   Tiles         Total pixels   Kelp pixels   Max. res. (m)    Min res. (m)      Avg. res. (m)   Stdev. res. (m)
=====   ===========   ============   ===========   ==============   ===============   =============   ===============
Train   54233         14216855552    1869302818    0.023            0.428             0.072           0.090
Val     3667          961282048      147658714     0.023            0.272             0.091           0.121
Test    4019          1053556736     156686376     0.023            0.068             0.040           0.020
=====   ===========   ============   ===========   ==============   ===============   =============   ===============


.. TODO: Details about mussels dataset


Metrics
--------

For all metrics, let:

:math:`A` equal the set of human-labelled pixels.

:math:`B` be defined as the set of pixel labels predicted by the model.

:math:`A_i` and :math:`B_i` be the sets of pixels for a particular class of interest, :math:`i` (from :math:`A` and :math:`B`).

Accuracy
    The ratio of counts of pixels correctly classified by the model divided over the total number of pixels in an image.


IoU
    The "intersection over union", also called the "Jaccard Index". Defined as:

    .. math::

        IoU_i (A,B) = \frac{|A_i \cap B_i|}{|A_i \cup B_i|}

Mean IoU
    The mean of the intersection over union values over all classes. Defined as:

    .. math::

        mIoU (A,B) = \frac{\sum_{i=1}^{c} IoU_{i}(A,B)}{c}

Training Details
----------------

Kelp
....
The `LRASPP MobileNetV3-Large <https://arxiv.org/abs/1905.02244>`_ was trained using a stochastic gradient descent optimizer
with a learning rate of :math:`0.35`, weight decay set to :math:`3 \times 10^{-6}`, for a total of 100 epochs. A
`cosine annealing learning rate schedule <https://arxiv.org/abs/1608.03983>`_ was used to improve accuracy. The loss function used was
`Focal Tversky Loss <https://arxiv.org/abs/1608.03983>`_, with parameters :math:`\alpha=0.7, \beta=0.3, \gamma=4.0 / 3.0`.

The model was trained on an AWS "p3.8xlarge" instance with 4 Nvidia Tesla V100 GPUS and required 18 hours and 1 minute to finish.
At the end of training, the model parameters which achieved the best mIoU score on the validation data split were saved. These
parameters were used to calculate the final performance statistics for the model (See `Performance Results`_).

Full source code for training the kelp model is available at https://github.com/tayden/hakai-ml-train

Performance Results
-------------------

+------------------+----------------------------------------------------------------+-------------------------+-------------+-------------+----------+----------+-------------+-------------+----------+----------+
| Tool             | Model Architecture                                             | Output Classes          | Validation                                      | Test                                            |
+                  +                                                                +                         +-------------+-------------+----------+----------+-------------+-------------+----------+----------+
|                  |                                                                |                         | Class 0 IoU | Class 1 IoU | Mean IoU | Accuracy | Class 0 IoU | Class 1 IoU | Mean IoU | Accuracy |
+==================+================================================================+=========================+=============+=============+==========+==========+=============+=============+==========+==========+
| ``find-kelp``    | `LRASPP MobileNetV3-Large <https://arxiv.org/abs/1905.02244>`_ | 0=background, 1=kelp    | 0.9437      | 0.6609      | 0.8023   | 0.9555   | 0.9286      | 0.5930      | 0.76077  | 0.93844  |
+------------------+----------------------------------------------------------------+-------------------------+-------------+-------------+----------+----------+-------------+-------------+----------+----------+
| ``find-mussels`` | `LRASPP MobileNetV3-Large <https://arxiv.org/abs/1905.02244>`_ | 0=background, 1=mussels | 0.9622      | 0.7188      | 0.8405   | 0.9678   | -           | -           | -        | -        |
+------------------+----------------------------------------------------------------+-------------------------+-------------+-------------+----------+----------+-------------+-------------+----------+----------+