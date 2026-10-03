# Preserved output capture-coordinate failure

The private native run passed its initial 94 checks and the output-move and
fractional-scale cases. It recorded fresh configuration generations and immutable
retained output facts, plus actual input-hole routing at 125% scale. It then failed
`rotatedInputHoleStillPaintsPeer` by probing the normalized grim image using raw
framebuffer coordinates. The captured image and compositor pointer implementation
show that these interfaces use normalized capture and logical absolute positions.

The failed 105-check packet is preserved unchanged in
`qa/native-1791067298818731029/report.json`; cleanup passed. The fresh V25 derivative
corrects capture/pointer coordinates, retains the original deadlines and intended
pixel/recipient assertions, and passes the complete run. This failed attempt does
not establish acceptance. No installed desktop was changed.
