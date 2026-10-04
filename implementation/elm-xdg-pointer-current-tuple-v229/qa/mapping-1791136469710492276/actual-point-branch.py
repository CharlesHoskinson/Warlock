if buffer['geometry'][:2] == [0, 0]:
    point = [fact['visualGeometry'][i] + local[i] for i in range(2)]
else:
    assert fact['visualGeometry'][2:] == buffer['geometry'][2:], 'Only selected Q1 geometry mapping supported'
    assert buffer['geometry'][:2] == requested['origin'], 'Committed origin differs from selected profile'
    point = [fact['visualGeometry'][i] + local[i] - buffer['geometry'][i] for i in range(2)]
