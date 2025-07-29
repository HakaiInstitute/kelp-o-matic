"""
Test cases to verify that window generation provides full coverage of input images,
especially for edge cases where the final rows/columns might be missed.
"""

import pytest
import numpy as np

from kelp_o_matic.processing import ImageProcessor
from kelp_o_matic.config import ProcessingConfig


class TestWindowGenerationCoverage:
    """Test coverage issues with window generation"""

    def test_problematic_image_dimensions(self):
        """Test image dimensions that previously caused missing final rows/columns"""
        problematic_cases = [
            # (height, width, tile_size, stride, description)
            (1000, 1000, 512, 256, "1000x1000 with 512 tiles and 256 stride"),
            (1500, 1200, 512, 256, "1500x1200 with 512 tiles and 256 stride"),
            (768, 768, 512, 256, "768x768 with 512 tiles and 256 stride"),
            (1024, 800, 256, 128, "1024x800 with 256 tiles and 128 stride"),
            (333, 777, 224, 112, "333x777 with 224 tiles and 112 stride"),
            (100, 150, 512, 256, "Small image smaller than tile size"),
        ]

        for height, width, tile_size, stride, description in problematic_cases:
            config = ProcessingConfig(
                crop_size=tile_size, batch_size=1, band_order=[1, 2, 3]
            )

            # Generate windows
            windows = list(ImageProcessor._generate_windows(height, width, config))

            # Validate full coverage
            is_covered = ImageProcessor._validate_full_coverage(height, width, windows)

            assert is_covered, (
                f"Failed coverage test for {description}: "
                f"Generated {len(windows)} windows for {height}x{width} image"
            )

    def test_edge_cases_small_images(self):
        """Test edge cases with very small images"""
        edge_cases = [
            (50, 50, 512, 256, "Tiny image much smaller than tile"),
            (1, 1, 224, 112, "Single pixel image"),
            (10, 1000, 224, 112, "Very narrow image"),
            (1000, 10, 224, 112, "Very tall image"),
        ]

        for height, width, tile_size, stride, description in edge_cases:
            config = ProcessingConfig(
                crop_size=tile_size, batch_size=1, band_order=[1, 2, 3]
            )

            windows = list(ImageProcessor._generate_windows(height, width, config))
            is_covered = ImageProcessor._validate_full_coverage(height, width, windows)

            assert is_covered, f"Failed coverage test for {description}"
            assert len(windows) > 0, f"No windows generated for {description}"

    def test_exact_multiples(self):
        """Test cases where dimensions are exact multiples of stride"""
        exact_cases = [
            (512, 512, 256, 128, "Exact 4x multiple"),
            (768, 768, 256, 128, "Exact 6x multiple"),
            (1024, 1024, 512, 256, "Exact 4x multiple large"),
        ]

        for height, width, tile_size, stride, description in exact_cases:
            config = ProcessingConfig(
                crop_size=tile_size, batch_size=1, band_order=[1, 2, 3]
            )

            windows = list(ImageProcessor._generate_windows(height, width, config))
            is_covered = ImageProcessor._validate_full_coverage(height, width, windows)

            assert is_covered, f"Failed coverage test for {description}"

    def test_coverage_map_detailed(self):
        """Test detailed coverage analysis for a specific problematic case"""
        height, width = 1000, 1000
        tile_size = 512

        config = ProcessingConfig(
            crop_size=tile_size, batch_size=1, band_order=[1, 2, 3]
        )

        windows = list(ImageProcessor._generate_windows(height, width, config))

        # Create detailed coverage map
        coverage = np.zeros((height, width), dtype=int)

        for window in windows:
            row_start = max(0, window.row_off)
            row_end = min(height, window.row_off + window.height)
            col_start = max(0, window.col_off)
            col_end = min(width, window.col_off + window.width)

            coverage[row_start:row_end, col_start:col_end] += 1

        # Every pixel should be covered at least once
        assert np.all(coverage > 0), (
            f"Some pixels not covered. "
            f"Uncovered pixels at rows: {np.where(np.any(coverage == 0, axis=1))[0].tolist()}, "
            f"cols: {np.where(np.any(coverage == 0, axis=0))[0].tolist()}"
        )

        # Check that edge pixels are covered (this was the original bug)
        assert coverage[-1, :].min() > 0, "Bottom edge pixels not covered"
        assert coverage[:, -1].min() > 0, "Right edge pixels not covered"
        assert coverage[0, :].min() > 0, "Top edge pixels not covered"
        assert coverage[:, 0].min() > 0, "Left edge pixels not covered"

    def test_extended_dimensions_consistency(self):
        """Test that extended dimensions calculation is consistent with window generation"""
        test_cases = [
            (1000, 1000, 512, 256),
            (768, 1024, 256, 128),
            (333, 777, 224, 112),
        ]

        for height, width, tile_size, stride in test_cases:
            config = ProcessingConfig(
                crop_size=tile_size, batch_size=1, band_order=[1, 2, 3]
            )

            # Calculate extended dimensions
            ext_height, ext_width = ImageProcessor._calculate_extended_dimensions(
                height, width, config
            )

            # Generate windows for extended dimensions
            windows = list(
                ImageProcessor._generate_windows(ext_height, ext_width, config)
            )

            # Validate that windows cover the original image
            is_covered = ImageProcessor._validate_full_coverage(height, width, windows)
            assert is_covered, (
                f"Extended dimensions ({ext_height}x{ext_width}) don't provide "
                f"full coverage for original ({height}x{width})"
            )

    def test_window_bounds_validation(self):
        """Test that all generated windows have valid bounds"""
        height, width = 1000, 800
        config = ProcessingConfig(crop_size=512, batch_size=1, band_order=[1, 2, 3])

        windows = list(ImageProcessor._generate_windows(height, width, config))

        for i, window in enumerate(windows):
            # Check that window has positive dimensions
            assert window.width > 0, f"Window {i} has zero/negative width: {window}"
            assert window.height > 0, f"Window {i} has zero/negative height: {window}"

            # Check that window starts within image bounds
            assert window.row_off >= 0, f"Window {i} starts before image: {window}"
            assert window.col_off >= 0, f"Window {i} starts before image: {window}"

            # Check that window doesn't start beyond image
            assert window.row_off < height, (
                f"Window {i} starts beyond image height: {window}"
            )
            assert window.col_off < width, (
                f"Window {i} starts beyond image width: {window}"
            )

    def test_boundless_reading_approach(self):
        """Test that boundless reading handles extended windows properly"""
        # Test case based on the error: raster of 13715x16208, requesting (12288,0) of size 2048x1024
        original_height, original_width = 16208, 13715
        crop_size = 2048

        config = ProcessingConfig(
            crop_size=crop_size, batch_size=1, band_order=[1, 2, 3]
        )

        # Calculate extended dimensions
        extended_height, extended_width = ImageProcessor._calculate_extended_dimensions(
            original_height, original_width, config
        )

        # Generate windows for extended dimensions
        windows = list(
            ImageProcessor._generate_windows(extended_height, extended_width, config)
        )

        # With boundless reading, windows can extend beyond original bounds
        # The key is that they still provide full coverage of the original image
        assert ImageProcessor._validate_full_coverage(
            original_height, original_width, windows
        )

        # Check that we have windows that cover the problematic areas
        found_bottom_edge = False
        found_right_edge = False

        for window in windows:
            # Check if this window covers the bottom edge of the original image
            if (
                window.row_off < original_height
                and window.row_off + window.height >= original_height
            ):
                found_bottom_edge = True

            # Check if this window covers the right edge of the original image
            if (
                window.col_off < original_width
                and window.col_off + window.width >= original_width
            ):
                found_right_edge = True

        assert found_bottom_edge, (
            "No window covers the bottom edge of the original image"
        )
        assert found_right_edge, "No window covers the right edge of the original image"

    def test_boundless_reading_with_specific_case(self):
        """Test that boundless reading handles the specific error case properly"""
        # Error: "Access window out of range in RasterIO(). Requested (12288,0) of size 2048x1024"
        original_height, original_width = 16208, 13715
        crop_size = 2048

        config = ProcessingConfig(
            crop_size=crop_size, batch_size=1, band_order=[1, 2, 3]
        )

        # Calculate extended dimensions
        extended_height, extended_width = ImageProcessor._calculate_extended_dimensions(
            original_height, original_width, config
        )

        # Generate windows for extended dimensions
        windows = list(
            ImageProcessor._generate_windows(extended_height, extended_width, config)
        )

        # Verify full coverage is maintained
        assert ImageProcessor._validate_full_coverage(
            original_height, original_width, windows
        )

        # The problematic window may exist, but boundless reading will handle it
        # by filling out-of-bounds areas with zeros

    def test_all_windows_have_correct_size(self):
        """Test that all generated windows have the correct tile size"""
        test_cases = [
            (16208, 13715, 2048, "Large image with 2048 tiles"),
            (1000, 1000, 512, "Medium image with 512 tiles"),
            (333, 777, 224, "Small image with 224 tiles"),
        ]

        for height, width, crop_size, description in test_cases:
            config = ProcessingConfig(
                crop_size=crop_size, batch_size=1, band_order=[1, 2, 3]
            )

            # Calculate extended dimensions
            extended_height, extended_width = (
                ImageProcessor._calculate_extended_dimensions(height, width, config)
            )

            # Generate windows
            windows = list(
                ImageProcessor._generate_windows(
                    extended_height, extended_width, config
                )
            )

            # Verify all windows have the correct size
            for i, window in enumerate(windows):
                assert window.width == crop_size, (
                    f"{description}: Window {i} has incorrect width: "
                    f"{window.width} != {crop_size} (window: {window})"
                )
                assert window.height == crop_size, (
                    f"{description}: Window {i} has incorrect height: "
                    f"{window.height} != {crop_size} (window: {window})"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
