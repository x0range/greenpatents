import scipy
import scipy.sparse
import numpy as np
import glob

def join_matrices(filenames, outputfile, zerofile):
    pcm = scipy.sparse.load_npz(zerofile)
    for i, filename in enumerate(filenames):
        print("parsing {0} of {1}".format(i, len(filenames)))
        pcm2 = scipy.sparse.load_npz(filename)
        expected_sum = np.sum(pcm) + np.sum(pcm2)
        pcm = pcm + pcm2
        try:
            assert expected_sum == np.sum(pcm), "expected sum does not match actual sum: {0} != {1}".format(expected_sum, np.sum(pcm))
        except:
            pass
    
    scipy.sparse.save_npz(outputfile, pcm)


# coarse
filenames = glob.glob("patent_classification_matrix_*.npz")
outputFileName = "patent_classification_matrix_all.npz"
zerofile = "patent_classification_matrix_0.npz"

join_matrices(filenames, outputFileName, zerofile)

# detailled
filenames = glob.glob("patent_detailed_classification_matrix_*.npz")
outputFileName = "patent_detailed_classification_matrix_all.npz"
zerofile = "patent_detailed_classification_matrix_0.npz"

join_matrices(filenames, outputFileName, zerofile)
