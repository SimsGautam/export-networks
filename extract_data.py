import urllib2
import ast

list_of_countries = ['usa']

response = urllib2.urlopen('http://atlas.media.mit.edu/hs07/export/2010/' + list_of_countries[0] + '/show/all/')
dump = response.read()

data_dictionary = ast.literal_eval(dump)
print data_dictionary['data'][0]

