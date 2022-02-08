# %%
import pandas

COUNTRY = 'Spain'

p_active_complete_db = pandas.read_csv(r'..\real_data\reducedgoogledataset.csv')
p_active_partial_db  = p_active_complete_db[p_active_complete_db['country_region']==COUNTRY]
# %%
