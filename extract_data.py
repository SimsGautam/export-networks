import urllib2
import ast
import numpy as np


def organize_data_by_countries(start_country, other_countries):
	'''
	start_country: country to begin recursive search (typically 'usa')
	other_countries: list of other countries known (initially ['usa'])

	recursively finds data of exports of countries, starting with start_country
	'''

	all_country_data = {}
	new_countries = []

	url = 'http://atlas.media.mit.edu/hs07/export/2010/' + start_country + '/show/all/'
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
			country_data, list_of_countries = organize_data_by_countries(country, other_countries + new_countries)
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
	return export_matrix


if __name__ == '__main__':

	data_by_countries, list_of_countries = organize_data_by_countries('usa', ['usa'])

	export_matrix = get_export_matrix(data_by_countries, list_of_countries)

	print export_matrix
