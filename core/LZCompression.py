# lz compression made by revel8n

def decompress_data(decomp):
    pos = 0
    to_remove = len(decomp)
    comp = bytearray(decomp)
    decomp = bytearray(decomp)

    try:
        while (pos < len(comp)):
            value = comp[pos]
            pos += 1
            size = value >> 1

            if (value & 1):
                offset = len(decomp) - comp[pos]
                pos += 1
                while (size > 0):
                    size -= 1
                    decomp.append(decomp[offset % len(decomp)])
                    offset += 1
            else:
                while (size > 0):
                    size -= 1
                    decomp.append(comp[pos % len(comp)])
                    pos += 1
    except Exception as e:
        print(e)
        import traceback
        print(traceback.format_exc())
        pass

    return decomp[to_remove:]

def compress_data(data, min_size = 3, max_size = 127, window_size = 255, start_size = 0):
    length = len(data)
    comp = bytearray(data)
    
    pos = min(start_size, length)
    start = 0
    size = pos

    markers = []

    while pos < length:
        prev = pos - 1

        prev_max = prev
        size_max = 0
        
        while (prev >= 0) and (prev >= pos - window_size):
            pos_curr = pos
            prev_curr = prev
            size_curr = 0
            
            while (pos_curr < length) and (size_curr < max_size):
                if (data[prev_curr] != data[pos_curr]):
                    break
            
                pos_curr += 1
                prev_curr += 1
                size_curr += 1
        
            if size_curr > size_max:
                prev_max = prev
                size_max = size_curr
            
            if (size_curr >= max_size) or (pos_curr >= length):
                break

            prev -= 1
    
        if size_max >= min_size:
            if size > 0:
                markers.append((start, size))
            
            offset = prev_max - pos

            markers.append((offset, size_max))

            pos += size_max
            start = pos
            size = 0
        else:
            pos += 1
            size += 1

            if (size > 0) and (size >= max_size):
                markers.append((start, size))
                start = pos
                size = 0
    
    if size > 0:
        markers.append((start, size))
        size = 0
    
    for marker in markers:
        pos = marker[0]
        size = marker[1]

        value = size << 1

        if pos < 0:
            value |= 1
            comp.append(value)
            comp.append(-pos)
        else:
            comp.append(value)
            comp.extend(data[pos:pos + size])

    return comp[length:]