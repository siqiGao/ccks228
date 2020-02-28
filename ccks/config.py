
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim



# load model
print ("Loading model:word2vec ......")
w2v_model = gensim.models.KeyedVectors.load_word2vec_format('./word2vec/baike.vectors.bin', binary=True)
