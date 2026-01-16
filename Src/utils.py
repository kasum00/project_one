def load_compatibility(path):
    outfits = []
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 3:
                continue
            label = int(parts[0])
            items = parts[1:]
            if label == 1:
                outfits.append(items)
    return outfits
