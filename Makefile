PG_DB = businesses

all : south_shore_businesses.csv south_shore_businesses.geojson		\
	71st_street_businesses.csv 71st_street_businesses.geojson 

$(PG_DB) :
	createdb $(PG_DB)
	psql -d $(PG_DB) -c "CREATE EXTENSION postgis"

CommAreas.zip :
	wget -O $@ "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=Original"

CommAreas.shp : CommAreas.zip
	unzip $<

retail.csv :
	wget -O $@ "https://data.cityofchicago.org/api/views/kukh-c9wt/rows.csv?accessType=DOWNLOAD"

business_licenses.csv :
	wget -O $@ "https://data.cityofchicago.org/api/views/r5kz-chrr/rows.csv?accessType=DOWNLOAD"

%.vrt : %.csv
	@echo \
	\<OGRVRTDataSource\> \
	  \<OGRVRTLayer name=\"$*\"\> \
	    \<SrcDataSource\>$<\</SrcDataSource\> \
	    \<GeometryType\>wkbPoint\</GeometryType\> \
	    \<LayerSRS\>WGS84\</LayerSRS\> \
	    \<GeometryField encoding=\"PointFromColumns\" x=\"LONGITUDE\" y=\"LATITUDE\"/\> \
	  \</OGRVRTLayer\> \
        \</OGRVRTDataSource\> > $@


community_areas : CommAreas.shp
	ogr2ogr -f "PostgreSQL" PG:dbname=$(PG_DB) -t_srs EPSG:4326 -select area_numbe,community -nlt PROMOTE_TO_MULTI -nln $@ $<
	touch $@

71st_street : 71st_street.shp
	ogr2ogr -f "PostgreSQL" PG:dbname=$(PG_DB) -t_srs EPSG:4326 -nlt PROMOTE_TO_MULTI -nln $@ $<
	touch $@

53rd_street : 53rd_street.shp
	ogr2ogr -f "PostgreSQL" PG:dbname=$(PG_DB) -t_srs EPSG:4326 -nlt PROMOTE_TO_MULTI -nln $@ $<
	touch $@

business_licenses : business_licenses.vrt
	ogr2ogr -f "PostgreSQL" PG:dbname=$(PG_DB) $<
	touch $@

south_shore_businesses.csv : community_areas business_licenses
	psql -d $(PG_DB) -c "COPY \
            (SELECT business_licenses.* \
             FROM business_licenses \
             INNER JOIN community_areas \
             ON ST_Intersects(business_licenses.wkb_geometry, community_areas.wkb_geometry) \
             WHERE community='SOUTH SHORE' \
                 AND \"license term expiration date\" != '' \
                 AND \"license term expiration date\"::DATE > NOW() \
             ORDER BY \"account number\"::NUMERIC,\"site number\"::NUMERIC) \
             TO STDOUT WITH CSV HEADER" | \
        csvcut -C 1,2 > $@

south_shore_businesses.geojson : community_areas business_licenses
	ogr2ogr -f "GeoJSON" $@ PG:dbname=$(PG_DB) -sql \
            "SELECT business_licenses.* \
             FROM business_licenses \
             INNER JOIN community_areas \
             ON ST_Intersects(business_licenses.wkb_geometry, community_areas.wkb_geometry) \
             WHERE community='SOUTH SHORE' \
                 AND \"license term expiration date\" != '' \
                 AND \"license term expiration date\"::DATE > NOW()"

71st_street_businesses.csv : 71st_street business_licenses
	psql -d $(PG_DB) -c "COPY \
            (SELECT business_licenses.* \
             FROM business_licenses \
             INNER JOIN \"71st_street\" \
             ON ST_Intersects(business_licenses.wkb_geometry, \"71st_street\".wkb_geometry) \
             WHERE \"license term expiration date\" != '' \
                 AND \"license term expiration date\"::DATE > NOW() \
             ORDER BY \"account number\"::NUMERIC,\"site number\"::NUMERIC) \
             TO STDOUT WITH CSV HEADER" | \
        csvcut -C 1,2 > $@

71st_street_businesses.geojson : 71st_street business_licenses
	ogr2ogr -f "GeoJSON" $@ PG:dbname=$(PG_DB) -sql \
            "SELECT business_licenses.* \
             FROM business_licenses \
             INNER JOIN \"71st_street\" \
             ON ST_Intersects(business_licenses.wkb_geometry, \"71st_street\".wkb_geometry) \
             WHERE \"license term expiration date\" != '' \
                 AND \"license term expiration date\"::DATE > NOW()"


53rd_street_businesses.csv : 53rd_street business_licenses
	psql -d $(PG_DB) -c "COPY \
            (SELECT business_licenses.* \
             FROM business_licenses \
             INNER JOIN \"53rd_street\" \
             ON ST_Intersects(business_licenses.wkb_geometry, \"53rd_street\".wkb_geometry) \
             WHERE \"license term expiration date\" != '' \
                 AND \"license term expiration date\"::DATE > NOW() \
             ORDER BY \"account number\"::NUMERIC,\"site number\"::NUMERIC) \
             TO STDOUT WITH CSV HEADER" | \
        csvcut -C 1,2 > $@

53rd_street_businesses.geojson : 53rd_street business_licenses
	ogr2ogr -f "GeoJSON" $@ PG:dbname=$(PG_DB) -sql \
            "SELECT business_licenses.* \
             FROM business_licenses \
             INNER JOIN \"53rd_street\" \
             ON ST_Intersects(business_licenses.wkb_geometry, \"53rd_street\".wkb_geometry) \
             WHERE \"license term expiration date\" != '' \
                 AND \"license term expiration date\"::DATE > NOW()"
