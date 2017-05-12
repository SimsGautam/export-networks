import urllib2
import ast
import numpy as np
import networkx as nx

def organize_data_by_countries(start_country, other_countries, year):
	'''
	start_country: country to begin recursive search (typically 'usa')
	other_countries: list of other countries known (initially ['usa'])

	recursively finds data of exports of countries, starting with start_country
	'''

	all_country_data = {}
	new_countries = []

	if year >= 2007:
		h = "hs07"
	elif year >= 2002:
		h = "hs02"
	elif year >= 1996:
		h = "hs96"
	elif year >= 1992:
		h = "hs92"
	url = 'http://atlas.media.mit.edu/'+h+'/export/'+ str(year) +'/' + start_country + '/show/all/'
	try:
		response = urllib2.urlopen(url)
	except:
		print('failed to grab: ' + url)
		return all_country_data, other_countries

	dump = response.read()
	data = ast.literal_eval(dump)['data']

	for datum in data:
		if datum['dest_id'][2:] not in other_countries:
			new_countries.append(datum['dest_id'][2:])

	# no new countries to search
	if len(new_countries) == 0:
		for datum in data:
			try:
				key = (datum['origin_id'][2:], datum['dest_id'][2:])
				value = datum['export_val']
				all_country_data[key] = value
			except:
				continue
		return all_country_data, other_countries # retuns empty dictionary

	else:
		for country in new_countries:
			# a.update(b) extends dictionary a with dictionary b
			# this is the recursive call to find other countries
			country_data, list_of_countries = organize_data_by_countries(country, other_countries + new_countries, year)
			all_country_data.update(country_data)

	return all_country_data, list_of_countries

def get_export_matrix(all_country_data, list_of_countries):
	'''
	returns the nxn numpy matrix for the export graph
	where n is the total number of countries and entry
	M_{ij} is the export from country i to country j
	'''
	list_of_countries = sorted(list_of_countries)
	n = len(list_of_countries)
	export_matrix = np.empty([n,n])
	for i,country_origin in enumerate(list_of_countries):
		for j, country_dest in enumerate(list_of_countries):
			if (country_origin, country_dest) in all_country_data:
				export_matrix[i,j] = all_country_data[(country_origin, country_dest)]
			else:
				export_matrix[i,j] = 0
	return export_matrix


def get_n_highest_centralities(centrality_dic, n):
	'''
	Given a dict from countries to centrality values, output the n tuples of (country, value) with highest values.
	'''
	all_tuples = []
	for key in centrality_dic.keys():
		all_tuples.append((key, centrality_dic[key]))
	all_tuples.sort(key=lambda x: x[1], reverse=True)
	return all_tuples[:n]

def get_centralities_dicts(graph):
	'''
	Output different centrality measures of the graph.
	'''
	betweenness = nx.betweenness_centrality(graph)
	eigen = nx.eigenvector_centrality(graph, max_iter= 10000, tol = 0.005)
	closeness = nx.closeness_centrality(graph)
	degree = nx.degree_centrality(graph)
	return {"betweenness": betweenness, "eigen": eigen, "closeness": closeness, "degree": degree}

def translate_number_to_country(numbers_to_countries, list_of_tuples):
	return [(numbers_to_countries[country], value) for country, value in list_of_tuples]

def get_all_centralities_given_year(year):
	'''
	Given a year returns a mapping from a centrality_string to a list of 10 tuples.
	Each tuple has a country and its corresponding centrality value.
	'''
	top_ten_per_centrality = {}
	data_by_countries, list_of_countries = organize_data_by_countries('usa', ['usa'], year)

	numbers_to_countries = {}
	sorted_countries = sorted(list_of_countries)	
	for i,country in enumerate(sorted_countries):
		numbers_to_countries[i] = country

	export_matrix = get_export_matrix(data_by_countries, list_of_countries)
	g = nx.Graph(export_matrix)

	centralities = get_centralities_dicts(g)
	for centrality_string in centralities.keys():
		highest_countries = get_n_highest_centralities(centralities[centrality_string], 10)
		country_value_tuples = translate_number_to_country(numbers_to_countries, highest_countries)
		top_ten_per_centrality[centrality_string] = country_value_tuples
	return top_ten_per_centrality


if __name__ == '__main__':

	for year in [1995, 2000, 2005, 2010,2015]:
		print get_all_centralities_given_year(year)

	import pdb; pdb.set_trace()
