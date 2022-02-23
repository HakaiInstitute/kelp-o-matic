from hakai_segmentation.managers import GeotiffSegmentation
from hakai_segmentation.models import KelpPresenceSegmentationModel, MusselPresenceSegmentationModel


def find_kelp(source: str, dest: str,
              crop_size: int = 256, padding: int = 128, batch_size: int = 2):
    """Detect kelp in source image and output the resulting classification raster to dest.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    """
    model = KelpPresenceSegmentationModel()
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size)()


def find_mussels(source: str, dest: str,
                 crop_size: int = 256, padding: int = 128, batch_size: int = 2):
    """Detect mussels in source image and output the resulting classification raster to dest.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    """

    model = MusselPresenceSegmentationModel()
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size)()