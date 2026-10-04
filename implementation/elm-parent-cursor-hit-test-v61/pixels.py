"""Read the single solid magenta cursor body, retaining unrelated-color diagnostics."""
def measure(width, height, channels, stride, raw):
    magenta = set(); cyan = set()
    for y in range(height):
        for x in range(width):
            i = y*stride+x*channels
            r,g,b = raw[i:i+3]
            if r>220 and g<35 and b>220: magenta.add((x,y))
            if r<35 and g>220 and b>220: cyan.add((x,y))
    pending = set(magenta); components = []
    while pending:
        stack = [next(iter(pending))]; body = []
        while stack:
            point = stack.pop()
            if point not in pending: continue
            pending.remove(point); body.append(point)
            x,y = point
            stack.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
        bounds = [min(x for x,y in body), min(y for x,y in body),
                  max(x for x,y in body)+1, max(y for x,y in body)+1]
        area = (bounds[2]-bounds[0])*(bounds[3]-bounds[1])
        if len(body)>=64 and area>=100 and len(body)/area>=.65:
            inside = [p for p in cyan if bounds[0]<=p[0]<bounds[2] and bounds[1]<=p[1]<bounds[3]]
            components.append({'bounds':bounds,'magenta':len(body),'cyan':len(inside)})
    selected = components[0] if len(components)==1 else {'bounds':None,'magenta':0,'cyan':0}
    return {'dimensions':[width,height], 'components':components, **selected,
            'rawMagenta':len(magenta), 'rawCyan':len(cyan)}

def pixels(path):
    import hashlib
    import gi
    gi.require_version('GdkPixbuf','2.0')
    from gi.repository import GdkPixbuf
    image = GdkPixbuf.Pixbuf.new_from_file(str(path))
    result = measure(image.get_width(),image.get_height(),image.get_n_channels(),
                     image.get_rowstride(),image.get_pixels())
    result['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result
