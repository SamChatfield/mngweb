var locations = [
  {"address": "Birmingham", "region": "GB"},
  {"address": "Coventry", "region": "GB"},
  {"address": "Ohio", "region": "US"},
];

function geocodeLocations(geocoder, resultsMap, locations) {
  var location;
  for (var i = 0; i < cities.length; i++) {
    location = locations[i];
    geocoder.geocode({'address': location.address, 'region': location.region}, function(results, status) {
    if (status === google.maps.GeocoderStatus.OK) {
      var marker = new google.maps.Marker({
        map: resultsMap,
        position: results[0].geometry.location
      });
    }
  });

}