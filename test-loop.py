# test loop

max_idx = 5
for idx in range(max_idx):

    print('idx: ' + str(idx))

    if idx > 0:
        idx = idx - 1
        print('changed idx: ' + str(idx))