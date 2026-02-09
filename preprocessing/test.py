from pandana.loaders import osm

network = osm.pdna_network_from_bbox(11.970291, 55.845085, 12.014236, 55.858888)

network.plot()

#test = network.nearest_pois(1000, category='restaurant')
#print(test)