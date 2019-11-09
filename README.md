# pwnagotchi State Api

Throw it into the plugins directory. 

At the moment it only has the `enabled: True` config option.

`/plugins/state-api/display` to retrieve the state.html

`/plugins/state-api/` to retrieve the JSON

# TODO
I'm wary of exposing too much from the internal API or changing its interface to 0.0.0.0, and want to keep external traffic to a minium. 

From the plugin, access the internal API for the following, and provide a **SUBSET** via json.

  `GET /api/v1/mesh/data` https://pwnagotchi.ai/api/local/#get-api-v1-mesh-data

  `GET /api/v1/mesh/peers` https://pwnagotchi.ai/api/local/#get-api-v1-mesh-peers
  
 
  
  
