# Tommy Carstensen, 2020-02-04

def main():

    path_bim = 'sha_afr.qc.bim'
    path_strand = 'H3Africa_2017_20021485_A1-b37.Ilmn.strand'

    d_bim_ID2pos = {}
    d_bim_pos2ID = {}
    print('read bim')
    with open(path_bim) as f:
        for line in f:
            l = line.rstrip().split()
            chrom = l[0]
            pos = l[3]
            ID = l[1]
            assert ID not in d_bim_ID2pos.keys()
            d_bim_ID2pos[ID] = (chrom, pos)
            try:
                d_bim_pos2ID[(chrom, pos)].add(ID)
            except KeyError:
                d_bim_pos2ID[(chrom, pos)] = {ID}

    d_strand_ID2pos = {}
    d_strand_pos2ID = {}
    print('read strand')
    with open(path_strand) as f:
        for line in f:
            l = line.rstrip().split()
            ID = l[0]
            chrom = l[1]
            pos = l[2]
            assert ID not in d_strand_ID2pos.keys()
            d_strand_ID2pos[ID] = (chrom, pos)
            try:
                d_strand_pos2ID[(chrom, pos)].add(ID)
            except KeyError:
                d_strand_pos2ID[(chrom, pos)] = {ID}

    s = ''
    print('modify strand')
    with open(path_strand) as f:
        for line in f:
            l = line.rstrip().split()
            ID = l[0]
            chrom = l[1]
            pos = l[2]

            # ID is present in both the bim and strand file.
            if ID in d_bim_ID2pos.keys():
                s += line
                continue

            # Position is not present in the bim file.
            if not (chrom, pos) in d_bim_pos2ID.keys():
                s += line
                continue

            # Some ID in the bim file match the current ID or some other ID in the strand file?
            # Don't modify current ID in the strand file.
            if len(d_bim_pos2ID[(chrom, pos)] & d_strand_pos2ID[(chrom, pos)]) > 0:
                s += line
                continue

            # Some ID in the bim file match *part of* the the current ID in the strand file?
            # Modify ID in the strand file.
            for ID_bim in d_bim_pos2ID[(chrom, pos)]:
                if ID_bim in ID or ID_bim.replace('rs', '') in ID:
                    if ID_bim in d_strand_ID2pos.keys():
                        match = True
                        l[0] = ID_bim
                        s += '\t'.join(l) + '\n'
                        # Add to dictionary to avoid duplicates being created in new modified strand file.
                        assert ID_bim not in d_strand_ID2pos.keys()
                        d_strand_ID2pos[ID_bim] = (chrom, pos)
                        break
            else:
                match = False
            if match is True:
                continue

            # Some ID in the bim file match (part of) some other ID in the strand file?
            # Don't modify current ID in the strand file.
            match = False
            for ID_bim in d_bim_pos2ID[(chrom, pos)]:
                for ID_strand in d_strand_pos2ID[(chrom, pos)]:
                    if any((
                        ID_bim in ID_strand,
                        ID_bim.replace('rs', '') in ID_strand,
                        )):
                        match = True
                        s += line
                        break
                if match is True:
                    break
            if match is True:
                continue

            s += line

            continue

    with open(path_strand[:-7] + 'modifiedIDs' + '.strand', 'w') as f:
        f.write(s)

if __name__ == '__main__':
    main()