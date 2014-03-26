import json
import urllib, urllib2


def music_query(search_terms):
	root_url = 'http://developer.echonest.com/api/v4/'
	source = 'song/search'
	search_terms = search_terms.replace(' ','+')
	echo_nest_api = '68NJWFXIG7UDXOTC2'
	search_url = "{0}{1}?api_key={2}&format=json&description=country&min_danceability=0.18&max_danceability=1&min_energy=0&max_energy=1&artist_max_familiarity=1&artist_min_familiarity=0.5&style={3}&results=20&sort=tempo-desc".format(
		root_url,
		source,
		echo_nest_api,
		search_terms)

	results = []
	try:
		response = urllib2.urlopen(search_url).read()
		json_response = json.loads(response)
		#print json_response['response']['songs']
		for song in json_response['response']['songs']:
			results.append({
				'artist':song['artist_name'],
				'title':song['title']
				})

	except urllib2.URLError, e:
		print "Error querying for song", e

	return results