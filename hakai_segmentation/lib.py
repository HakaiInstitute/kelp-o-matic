from hakai_segmentation.managers import GeotiffSegmentation
from hakai_segmentation.models import KelpPresenceSegmentationModel, MusselPresenceSegmentationModel


def find_kelp(source: str, dest: str,
              crop_size: int = 256, padding: int = 128, batch_size: int = 2, no_gpu: bool = False):
    """Detect kelp in image at path `source` and output the resulting classification raster to file at path `dest`.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    :param no_gpu: Disable Cuda GPU usage and run on CPU only.
    """
    model = KelpPresenceSegmentationModel(no_gpu=no_gpu)
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size)()


def find_mussels(source: str, dest: str,
                 crop_size: int = 256, padding: int = 128, batch_size: int = 2, no_gpu: bool = False):
    """Detect mussels in image at path `source` and output the resulting classification raster to file at path `dest`.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    :param no_gpu: Disable Cuda GPU usage and run on CPU only.
    """

    model = MusselPresenceSegmentationModel(no_gpu=no_gpu)
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size)()
