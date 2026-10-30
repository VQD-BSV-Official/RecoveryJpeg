def create_new_size(w = 6000, h = 3512):
    return w.to_bytes(2, 'big'), h.to_bytes(2, 'big')


def main():
    w_bytes, h_bytes = create_new_size()
    print(h_bytes.hex())

main()