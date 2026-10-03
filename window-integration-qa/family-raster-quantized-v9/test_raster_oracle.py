import hashlib
import tempfile
from pathlib import Path
import unittest

from raster_oracle import bilinear, compare, encode_png, png_rgba, premultiply, render


class RasterEvidenceTests(unittest.TestCase):
    output = {"x": 0, "y": 0, "width": 4, "height": 4, "bufferWidth": 4, "bufferHeight": 4}

    def member(self, pixels, size, rect):
        return {"pixels": size, "premultiplied": premultiply(pixels), "rectangle": dict(zip(("x", "y", "width", "height"), rect))}

    def scene(self):
        # Handdeclared asymmetric owner and opaque modal child.
        owner = bytes((200, 0, 0, 255)) * 16
        child = bytes((0, 0, 200, 255)) * 4
        return [self.member(owner, (4, 4), (0, 0, 4, 4)), self.member(child, (2, 2), (1, 0, 2, 2))]

    def test_full_owner_child_raster_matches_handdeclared_grid(self):
        red, blue = bytes((200, 0, 0, 255)), bytes((0, 0, 200, 255))
        expected = red + blue + blue + red + red + blue + blue + red + red * 8
        self.assertEqual(render(self.output, self.scene()), expected)
        self.assertEqual(compare(expected, expected, 4, 4)["channelsCompared"], 64)

    def test_missing_child_fails_all_four_child_pixels(self):
        expected = render(self.output, self.scene())
        wrong = render(self.output, self.scene()[:1])
        self.assertEqual(compare(wrong, expected, 4, 4)["badPixels"], 4)

    def test_wrong_composite_order_fails(self):
        expected = render(self.output, self.scene())
        self.assertFalse(compare(render(self.output, self.scene()[::-1]), expected, 4, 4)["passed"])

    def test_shift_fails_even_at_quantization_bound(self):
        expected = render(self.output, self.scene())
        wrong = expected[4:] + expected[:4]
        self.assertFalse(compare(wrong, expected, 4, 4, 1)["passed"])

    def test_orientation_marks_detect_both_flips(self):
        original = b"".join(bytes((i * 12, 48, 0, 255)) for i in range(16))
        horizontal = b"".join(original[(y * 4 + x) * 4:(y * 4 + x + 1) * 4] for y in range(4) for x in range(3, -1, -1))
        vertical = b"".join(original[y * 16:(y + 1) * 16] for y in range(3, -1, -1))
        for flipped in (horizontal, vertical):
            self.assertFalse(compare(flipped, original, 4, 4, 1)["passed"])

    def test_premultiplied_translucent_child_uses_source_over(self):
        owner = self.member(bytes((200, 0, 0, 255)), (1, 1), (0, 0, 4, 4))
        child = self.member(bytes((0, 200, 0, 128)), (1, 1), (0, 0, 4, 4))
        expected = bytes((100, 100, 0, 255)) * 16
        self.assertEqual(render(self.output, [owner, child]), expected)
        wrong_alpha = bytes((0, 200, 0, 255)) * 16
        self.assertFalse(compare(wrong_alpha, expected, 4, 4, 1)["passed"])

    def test_half_texel_linear_sampling_has_handcomputed_average(self):
        source = bytes((0, 0, 0, 255, 200, 0, 0, 255, 0, 200, 0, 255, 200, 200, 0, 255))
        self.assertEqual(bilinear(source, 2, 2, 0.5, 0.5), (100, 100, 0, 255))
        self.assertEqual(bilinear(source, 2, 2, 0.125, 0.125), (0, 0, 0, 255))

    def test_output_origin_and_pixel_center_clipping(self):
        output = {**self.output, "x": 10, "y": 20}
        member = self.member(bytes((200, 0, 0, 255)), (1, 1), (9, 19, 2, 2))
        self.assertEqual(render(output, [member]), bytes((200, 0, 0, 255)) + bytes((0, 0, 0, 255)) * 15)

    def test_fractional_surface_extent_samples_actual_buffer_centers(self):
        output = {"x": 0, "y": 0, "width": 2, "height": 2, "bufferWidth": 3, "bufferHeight": 3}
        member = self.member(bytes((240, 0, 0, 255)), (1, 1), (0, 0, 2, 2))
        self.assertEqual(render(output, [member]), bytes((240, 0, 0, 255)) * 9)

    def test_bound_is_applied_to_every_channel_without_pixel_exclusion(self):
        expected = bytes((0, 0, 0, 255)) * 16
        quantized = bytes((1, 1, 1, 254)) * 16
        self.assertTrue(compare(quantized, expected, 4, 4, 1)["passed"])
        outlier = quantized[:-4] + bytes((2, 0, 0, 255))
        result = compare(outlier, expected, 4, 4, 1)
        self.assertFalse(result["passed"])
        self.assertEqual(result["firstFailures"][0]["x"], 3)
        self.assertEqual(result["firstFailures"][0]["y"], 3)
        with self.assertRaises(ValueError):
            compare(quantized, expected, 4, 4, 2)

    def test_decode_matches_original_and_rejects_foreign_bytes_extent(self):
        material = bytes((200, 12, 100, 255, 1, 2, 3, 128))
        png = encode_png(2, 1, material)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.png"
            path.write_bytes(png)
            digest = hashlib.sha256(png).hexdigest()
            self.assertEqual(png_rgba(path, digest, (2, 1)), material)
            with self.assertRaises(ValueError):
                png_rgba(path, "0" * 64, (2, 1))
            with self.assertRaises(ValueError):
                png_rgba(path, digest, (1, 2))

    def test_full_extent_and_nonfinite_rectangles_fail_closed(self):
        with self.assertRaises(ValueError):
            compare(bytes(16), bytes(16), 4, 4)
        member = self.member(bytes((200, 0, 0, 255)), (1, 1), (float("nan"), 0, 2, 2))
        with self.assertRaises(ValueError):
            render(self.output, [member])


if __name__ == "__main__":
    unittest.main()
