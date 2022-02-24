import fire

from hakai_segmentation.lib import find_kelp, find_mussels


def cli():
    """Run the python-fire CLI."""
    fire.Fire({
        "find-mussels": find_mussels,
        "find-kelp": find_kelp
    })


if __name__ == '__main__':
    cli()
