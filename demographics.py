import json
import census_area
import collections

CENSUS_KEY = 'ac94ba69718a7e1da4f89c6d218b8f6b5ae9ac49'

with open('commareas.geojson') as f:
    comm_areas = json.load(f)

south_shore, = [area for area in comm_areas['features']
                if area['properties']['COMMUNITY'] == 'SOUTH SHORE']


TOTAL = 'B01001_001E'

AGE = {'B01001_003E' : (0, 9),          
       'B01001_004E' : (0, 9),          
       'B01001_005E' : (10, 17),         
       'B01001_006E' : (10, 17),         
       'B01001_007E' : (18, 64),         
       'B01001_008E' : (18, 64),         
       'B01001_009E' : (18, 64),         
       'B01001_010E' : (18, 64),         
       'B01001_011E' : (18, 64),         
       'B01001_012E' : (18, 64),         
       'B01001_013E' : (18, 64),         
       'B01001_014E' : (18, 64),         
       'B01001_015E' : (18, 64),         
       'B01001_016E' : (18, 64),         
       'B01001_017E' : (18, 64),         
       'B01001_018E' : (18, 64),         
       'B01001_019E' : (18, 64),         
       'B01001_020E' : (65, float('inf')),
       'B01001_021E' : (65, float('inf')),
       'B01001_022E' : (65, float('inf')),
       'B01001_023E' : (65, float('inf')),
       'B01001_024E' : (65, float('inf')),
       'B01001_025E' : (65, float('inf')),
       'B01001_027E' : (0, 9),            
       'B01001_028E' : (0, 9),           
       'B01001_029E' : (10, 17),         
       'B01001_030E' : (10, 17),         
       'B01001_031E' : (18, 64),         
       'B01001_032E' : (18, 64),         
       'B01001_033E' : (18, 64),         
       'B01001_034E' : (18, 64),         
       'B01001_035E' : (18, 64),         
       'B01001_036E' : (18, 64),         
       'B01001_037E' : (18, 64),         
       'B01001_038E' : (18, 64),         
       'B01001_039E' : (18, 64),         
       'B01001_040E' : (18, 64),         
       'B01001_041E' : (18, 64),         
       'B01001_042E' : (18, 64),         
       'B01001_043E' : (18, 64),         
       'B01001_044E' : (65, float('inf')),
       'B01001_045E' : (65, float('inf')),
       'B01001_046E' : (65, float('inf')),
       'B01001_047E' : (65, float('inf')),
       'B01001_048E' : (65, float('inf')),
       'B01001_049E' : (65, float('inf'))}

c = census_area.Census(CENSUS_KEY)

total = c.acs5.geo(TOTAL,
                   south_shore['geometry'],
                   year = 2014)[TOTAL]


ages_by_sex = c.acs5.geo(tuple(AGE),
                         south_shore['geometry'],
                         year = 2014)

ages = collections.defaultdict(int)
for var, bucket in AGE.items():
    ages[bucket] += ages_by_sex[var]

for bucket in ages:
    ages[bucket] /= total

INCOME = {'B25120_001E': 'Aggregate household income in the past 12 months (in 2015 Inflation-adjusted dollars)',
          'B19001_001E': 'Total Households',
          'B19001_002E': (0, 9999),
          'B19001_003E': (10000, 14999),
          'B19001_004E': (15000, 19999),
          'B19001_005E': (20000, 24999),
          'B19001_006E': (25000, 29999),
          'B19001_007E': (30000, 34999),
          'B19001_008E': (35000, 39999),
          'B19001_009E': (40000, 44999),
          'B19001_010E': (45000, 49999),
          'B19001_011E': (50000, 59999),
          'B19001_012E': (60000, 74999),
          'B19001_013E': (75000, 99999),
          'B19001_014E': (100000, 124999),
          'B19001_015E': (125000, 149999),
          'B19001_016E': (150000, 199999),
          'B19001_017E': (200000, float('inf'))}
          
income = c.acs5.geo(tuple(INCOME),
                    south_shore['geometry'],
                    year = 2014,
                    ignore_missing=True)

print(sorted(income.items()))
per_household = income['B25120_001E']/income['B19001_001E']

print(per_household)

                        


