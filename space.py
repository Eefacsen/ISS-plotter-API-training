import pandas as pd
import json
import plotly.express as px

# set API location
url = 'http://api.open-notify.org/iss-now.json'
# create a DF from the API issued json file
df = pd.read_json(url)

# set new colums latitude and longitude from the index's -> lat and long
df['latitude'] = df.loc['latitude', 'iss_position']
df['longitude'] = df.loc['longitude', 'iss_position']
# reset DF index to default 0-9, this means main index is not needed to be long and lat
df.reset_index(inplace=True)
# now drop unwanted colums being index(long, lat) and message(success)
df = df.drop(['index', 'message'], axis=1)  # i dont understand second argumnet > axis=1
# using plotly scatter_geo we can plot markers on a world map
fig = px.scatter_geo(df, lat='latitude', lon='longitude')

fig.show()


