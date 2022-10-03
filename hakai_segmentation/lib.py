from hakai_segmentation.managers import GeotiffSegmentation
from hakai_segmentation.models import KelpPresenceSegmentationModel, KelpSpeciesSegmentationModel, \
    MusselPresenceSegmentationModel


def find_kelp(source: str, dest: str, species: bool = False,
              crop_size: int = 256, padding: int = 128, batch_size: int = 2, use_gpu: bool = True,
              reload_model_on_batch: bool = False):
    """Detect kelp in image at path `source` and output the resulting classification raster to file at path `dest`.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param species: Do species classification instead of presence/absence.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    :param use_gpu: Disable Cuda GPU usage and run on CPU only.
    :param reload_model_on_batch: Experimental flag to reload the model for each data batch. May resolve memory issues.
    """
    if species:
        model = KelpSpeciesSegmentationModel(use_gpu=use_gpu)
    else:
        model = KelpPresenceSegmentationModel(use_gpu=use_gpu)
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size,
                        reload_model_on_batch=reload_model_on_batch)()


def find_mussels(source: str, dest: str,
                 crop_size: int = 256, padding: int = 128, batch_size: int = 2, use_gpu: bool = True,
                 reload_model_on_batch: bool = False):
    """Detect mussels in image at path `source` and output the resulting classification raster to file at path `dest`.

    :param source: Input image with Byte data type.
    :param dest: File path location to save output to.
    :param crop_size: The size of cropped image square run through the segmentation model.
    :param padding: The number of context pixels added to each side of the cropped image squares.
    :param batch_size: The batch size of cropped image sections to process together.
    :param use_gpu: Disable Cuda GPU usage and run on CPU only.
    :param reload_model_on_batch: Experimental flag to reload the model for each data batch. May resolve memory issues.
    """
    model = MusselPresenceSegmentationModel(use_gpu=use_gpu)
    GeotiffSegmentation(model, source, dest,
                        crop_size=crop_size, padding=padding, batch_size=batch_size,
                        reload_model_on_batch=reload_model_on_batch)()
