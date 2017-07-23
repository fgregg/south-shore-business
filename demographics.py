import json
import census_area
import collections
import census.math

def aggregate_by_common_value(d, D):
    agg = collections.defaultdict(int)
    for var, bucket in D.items():
        agg[bucket] += d[var]

    return agg

def ages(acs, geo, year, **kwargs):
    TOTAL = 'B01001_001E'
    AGE = {'B01001_003E' : 'Ages: 0-9',          
           'B01001_004E' : 'Ages: 0-9',          
           'B01001_005E' : 'Ages: 10-17',         
           'B01001_006E' : 'Ages: 10-17',         
           'B01001_007E' : 'Ages: 18-64',         
           'B01001_008E' : 'Ages: 18-64',         
           'B01001_009E' : 'Ages: 18-64',         
           'B01001_010E' : 'Ages: 18-64',         
           'B01001_011E' : 'Ages: 18-64',         
           'B01001_012E' : 'Ages: 18-64',         
           'B01001_013E' : 'Ages: 18-64',         
           'B01001_014E' : 'Ages: 18-64',         
           'B01001_015E' : 'Ages: 18-64',         
           'B01001_016E' : 'Ages: 18-64',         
           'B01001_017E' : 'Ages: 18-64',         
           'B01001_018E' : 'Ages: 18-64',         
           'B01001_019E' : 'Ages: 18-64',         
           'B01001_020E' : 'Ages: 65+',
           'B01001_021E' : 'Ages: 65+',
           'B01001_022E' : 'Ages: 65+',
           'B01001_023E' : 'Ages: 65+',
           'B01001_024E' : 'Ages: 65+',
           'B01001_025E' : 'Ages: 65+',
           'B01001_027E' : 'Ages: 0-9',            
           'B01001_028E' : 'Ages: 0-9',           
           'B01001_029E' : 'Ages: 10-17',         
           'B01001_030E' : 'Ages: 10-17',         
           'B01001_031E' : 'Ages: 18-64',         
           'B01001_032E' : 'Ages: 18-64',         
           'B01001_033E' : 'Ages: 18-64',         
           'B01001_034E' : 'Ages: 18-64',         
           'B01001_035E' : 'Ages: 18-64',         
           'B01001_036E' : 'Ages: 18-64',         
           'B01001_037E' : 'Ages: 18-64',         
           'B01001_038E' : 'Ages: 18-64',         
           'B01001_039E' : 'Ages: 18-64',         
           'B01001_040E' : 'Ages: 18-64',         
           'B01001_041E' : 'Ages: 18-64',         
           'B01001_042E' : 'Ages: 18-64',         
           'B01001_043E' : 'Ages: 18-64',         
           'B01001_044E' : 'Ages: 65+',
           'B01001_045E' : 'Ages: 65+',
           'B01001_046E' : 'Ages: 65+',
           'B01001_047E' : 'Ages: 65+',
           'B01001_048E' : 'Ages: 65+',
           'B01001_049E' : 'Ages: 65+'}
    
    total = acs.geo(TOTAL, geo, year=year, **kwargs)[TOTAL]
    ages_by_sex = acs.geo(tuple(AGE), geo, year=year, **kwargs)

    ages = aggregate_by_common_value(ages_by_sex, AGE)
    
    for bucket in ages:
        ages[bucket] /= total

    return ages

def income(acs, geo, year, **kwargs):
        
    INCOME = {'B19001_002E': (0, 9999),
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
    
    income = acs.geo(tuple(INCOME), geo, year=year,
                     ignore_missing=True, **kwargs)
    
    income_counts = [(income[k], v) for k, v in INCOME.items()]
    total_households = sum(income.values())
    median_household_income = census.math.pareto_percentile(income_counts)
    
    bin_percent = lambda x, y: sum(income[k] for k, (lower, upper) in INCOME.items()
                                   if lower >= x and upper <= y)/total_households
    results = {"Household Income, 100K +": bin_percent(100000, float('inf')),
               "Household Income, 75-100K": bin_percent(75000, 100000),
               "Household Income, 50-75K": bin_percent(50000, 75000),
               "Household Income, 35-50K": bin_percent(35000, 50000),
               "Household Income, 20-35K": bin_percent(20000, 35000),
               "Household Income, 0-20K": bin_percent(0, 20000),
               "Household Income, Median": median_household_income}


    return results

def per_household(acs, geo, year, **kwargs):
    AGG_INCOME = {'B19025_001E': 'Aggregate household income in the past 12 months (in 2015 Inflation-adjusted dollars)',
                  'B19051_001E': 'total'}

    agg_income = acs.geo(tuple(AGG_INCOME), geo, year=year,
                         ignore_missing=True, **kwargs)


    aggregate_income = agg_income.pop('B19025_001E')
    total_households = agg_income.pop('B19051_001E')
 
    return {"Household Income, Average": aggregate_income/total_households}



def unemployment(acs, geo, year, **kwargs):
        
    # 16 through 24
    LABOR_FORCE = ['B23001_004E',
                   'B23001_011E',
                   'B23001_018E',
                   'B23001_090E',
                   'B23001_097E',
                   'B23001_104E']
    
    UNEMPLOYED = ['B23001_008E',
                  'B23001_015E',
                  'B23001_022E',
                  'B23001_094E',
                  'B23001_101E',
                  'B23001_108E']
    
    employment = acs.geo(LABOR_FORCE + UNEMPLOYED,
                         geo, year=year,
                         ignore_missing=True, **kwargs)
    
    labor_force_16_24 = sum(employment[k] for k in LABOR_FORCE)
    unemployed_16_24 = sum(employment[k] for k in UNEMPLOYED)
    
    return {'Employment, Proportion of 16-24 years olds unemployed': unemployed_16_24/labor_force_16_24}

def race(acs, geo, year, **kwargs):
    RACE = {'B03002_001E': 'Race, Total',
            'B03002_003E': 'Race, Non-Hispanic White',
            'B03002_004E': 'Race, Non-Hispanic Black',
            'B03002_012E': 'Race, Hispanic'}
    
    race = acs.geo(tuple(RACE),
                   geo, year=year,
                   ignore_missing=True, **kwargs)
    
    total = race['B03002_001E']
    
    return {v: race[k]/total for k, v in RACE.items()}

def structures(acs, geo, year, **kwargs):
    STRUCTURES = {'B25024_001E': 'Housing Units, Total',
                  'B25024_002E': 'Housing Units, 1 unit, detached',
                  'B25024_003E': 'Housing Units, 1 unit, attached',
                  'B25024_004E': 'Housing Units, 2 unit',
                  'B25024_005E': 'Housing Units, 3 or 4 units',
                  'B25024_006E': 'Housing Units, 5 to 9 units',
                  'B25024_007E': 'Housing Units, 10-19 units',
                  'B25024_008E': 'Housing Units, 20-49 units',
                  'B25024_009E': 'Housing Units, 50+ units'}
    
    structures = acs.geo(tuple(STRUCTURES),
                         geo, year=year,
                         ignore_missing=True, **kwargs)
    
    total = structures['B25024_001E']
    
    return {v: structures[k]/total for k, v in STRUCTURES.items()}

def tenure(acs, geo, year, **kwargs):
    TENURE = {'B25003_001E': 'total',
              'B25003_002E': 'owner occupied',
              'B25003_003E': 'renter'}
    
    tenure = acs.geo(tuple(TENURE),
                     geo, year = year,
                     ignore_missing=True, **kwargs)
    
    total = tenure['B25003_001E']
    
    return {v: tenure[k]/total for k, v in TENURE.items()}

def tenure_by_structure(acs, geo, year, **kwargs):
    TENURE_BY_STRUCTURE = {'B25032_001E': 'total',
                           'B25032_002E': 'owner occupied',
                           'B25032_003E': 'owner occupied - single',
                           'B25032_004E': 'owner occupied - single',
                           'B25032_005E': 'owner occupied - multifamily',
                           'B25032_006E': 'owner occupied - multifamily',
                           'B25032_007E': 'owner occupied - multifamily',
                           'B25032_008E': 'owner occupied - multifamily',
                           'B25032_009E': 'owner occupied - multifamily',
                           'B25032_010E': 'owner occupied - multifamily'}
    
    tenure_by_structure = acs.geo(tuple(TENURE_BY_STRUCTURE),
                                  geo, year=year,
                                  ignore_missing=True, **kwargs)
    
    tenure_by_structure = aggregate_by_common_value(tenure_by_structure,
                                                    TENURE_BY_STRUCTURE)
    
    total = tenure_by_structure['total']
    
    return {k: v/total for k, v in tenure_by_structure.items()}
    
if __name__ == '__main__':
    import csv
    import sys
    
    CENSUS_KEY = 'ac94ba69718a7e1da4f89c6d218b8f6b5ae9ac49'

    with open('commareas.geojson') as f:
        comm_areas = json.load(f)

    south_shore, = [area for area in comm_areas['features']
                    if area['properties']['COMMUNITY'] == 'SOUTH SHORE']

    c = census_area.Census(CENSUS_KEY)

    header = False
    
    for year in (2015, 2010):
        row = {}
        for f in (unemployment, income, per_household, ages, race, structures, tenure, tenure_by_structure):
            row.update(f(c.acs5, south_shore['geometry'], year))

        if not header:
            writer = csv.DictWriter(sys.stdout, fieldnames=sorted(row))
            writer.writeheader()
            header = True

        writer.writerow(row)


    for year in (2000,):
        row = {}
        for f in (unemployment, per_household, ages, race, structures, tenure, tenure_by_structure):
            row.update(f(c.sf3, south_shore['geometry'], year, as_acs=True))

        writer.writerow(row)
