from housedata import *


dict_data = pd.read_pickle('/home/benmo/Data/Databases/CREA/data.pkl')
summ_data = pd.read_pickle('/home/benmo/Data/Databases/CREA/collecteddata.pkl')


test = explode_data(dict_data)
    