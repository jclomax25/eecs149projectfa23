"""
Fire Spread Model + Fire Ratings

Resources used
https://www.fs.usda.gov/rm/pubs_series/rmrs/gtr/rmrs_gtr371.pdf
https://www.prairieprojectknowledgehub.org/books/fire/page/rothermels-simple-fire-model#bkmrk-python-code
"""

import math
import random
import csv
import statistics
from datetime import datetime, timedelta, timezone

def get_simple_fire_spread(fuelload, fueldepth, windspeed, slope, fuelmoisture, fuelsav):
    """ model the rothermel surface fire spread on simplified parameters
        model is based on fundamental physical processes that dictate surface fire behavior
        @param fuelload
        @param fueldepth
        @param windspeed mph
        @param slope
        @param fuelmoisture
        @param fuelsav (SA to volume)
        @return Rate of spread (ft/min)
                Reaction Intensity (Btu/ft/min)
                Fireline Intensity (Btu/ft)
    """
    
    # Parameters
    maxval= 0
    if fuelload > 0:
        wo = fuelload # Ovendry fuel loading in (lb/ft^2). Amount of primary prod???
        fd = fueldepth # Fuel depth (ft)
        wv = windspeed * 88# Wind velocity at midflame height (ft/minute) = 88 * mph
        fpsa = fuelsav  # Fuel Particle surface area to volume ratio (1/ft)
        mf = fuelmoisture  # Fuel particle moisture content
        h = 8000  # Fuel particle low heat content
        pp = 32.  # Ovendry particle density
        st = 0.0555  # Fuel particle mineral content
        se = 0.010  # Fuel Particle effective mineral content
        mois_ext = 0.12  # Moisture content of extinction or 0.3 if dead
        #calculate slope as degrees
        slope_rad = math.atan(slope)
        slope_degrees = slope_rad / 0.0174533 #radians
        tan_slope = math.tan(slope_rad) #  in radians
        # Betas Packing ratio
        Beta_op = 3.348 * math.pow(fpsa, -0.8189)  # Optimum packing ratio
        ODBD = wo / fd  # Ovendry bulk density
        Beta = ODBD / pp #Packing ratio
        #Beta = 0.00158
        Beta_rel = Beta / Beta_op
        # Reaction Intensity
        WN = wo / (1 + st)  # Net fuel loading
        #A = 1 / (4.774 * pow(fpsa, 0.1) - 7.27)  # Unknown const
        A =  133.0 / math.pow(fpsa, 0.7913) #updated A
        T_max = math.pow(fpsa,1.5) * math.pow(495.0 + 0.0594 * math.pow(fpsa, 1.5),-1.0)  # Maximum reaction velocity
        #T_max = (fpsa*math.sqrt(fpsa)) / (495.0 + 0.0594 * fpsa * math.sqrt(fpsa))
        T = T_max * math.pow((Beta / Beta_op),A) * math.exp(A * (1 - Beta / Beta_op))  # Optimum reaction velocity
        # moisture dampning coefficient
        NM = 1. - 2.59 * (mf / mois_ext) + 5.11 * math.pow(mf / mois_ext, 2.) - 3.52 * math.pow(mf / mois_ext,3.)  # Moisture damping coeff.
        # mineral dampning
        NS = 0.174 * math.pow(se, -0.19)  # Mineral damping coefficient
        #print(T, WN, h, NM, NS)
        RI = T * WN * h * NM * NS
        #RI = 874
        # Propogating flux ratio
        PFR = math.pow(192.0 + 0.2595 * fpsa, -1) * math.exp(
            (0.792 + 0.681 * fpsa ** 0.5) * (Beta + 0.1))  # Propogating flux ratio
        ## Wind Coefficient
        B = 0.02526 * math.pow(fpsa, 0.54)
        C = 7.47 * math.exp(-0.1333 * math.pow(fpsa, 0.55))
        E = 0.715 * math.exp(-3.59 * 10**-4 * fpsa)
        #WC = C * wv**B * math.pow(Beta / Beta_op, -E) #wind coefficient
        if wv > (0.9 * RI): #important - don't know source. Matches BEHAVE
            wv = 0.9 * RI
        WC = (C * wv ** B) * math.pow((Beta / Beta_op), (-E))
        #WC= WC*0.74
        #Slope  coefficient
        SC = 5.275*(Beta**-0.3)*tan_slope**2
        #Heat sink

        EHN = math.exp(-138. / fpsa)  # Effective Heating Number = f(surface are volume ratio)
        QIG = 250. + 1116. * mf  # Heat of preignition= f(moisture content)
        # rate of spread (ft per minute)
        #RI = BTU/ft^2
        numerator = (RI * PFR * (1 + WC + SC))
        denominator = (ODBD * EHN * QIG)
        R = numerator / denominator #WC and SC will be zero at slope = wind = 0
        RT = 384.0/fpsa
        HA = RI*RT
        #fireline intensity as described by Albini via USDA Forest Service RMRS-GTR-371. 2018
        FI = (384.0/fpsa)*RI*(R) ##Uses Reaction Intensity in BTU / ft/ min
        #FI = HA*R
        if (RI <= 0):
            return (maxval, maxval, maxval)
        return (R, RI, FI)
    else:
        return (maxval, maxval, maxval)
    

def classify_ros_value(ros: float) -> str:
    """ classify the ros value based on NWCG values
        compare to IFTDSS values

        expects values to be in chain/hr units
    """
    if ros >= 0 and ros <= 5:
        return "Low"
    elif ros > 5 and ros <= 50:
        return "Moderate To High"
    else:
        # ros > 50 and ros <= 150:
        return "Very High to Extreme"
    
def ft_min_to_chain_hr(ros: float) -> float:
    """ ros converstion
    """
    feet_per_chain = 66.0
    minutes_per_hour = 60.0
    chains_per_hour = (ros * minutes_per_hour) / feet_per_chain
    return chains_per_hour


def pick_fuel_type(cats: list) -> str:
    """ if a lat lon read returns multiple fuel types
        exclude NB type
        then ranodomly pick
    """
    assert len(cats) != 0, "No fuel types detected, empty arr"
    if len(cats) == 1:
        return cats[0]

    containing_NB = [s for s in cats if "NB" in s]
    if len(containing_NB) == len(cats):
        return random.choice(cats)
    else:
        filtered_strings = [s for s in cats if "NB" not in s]
        return random.choice(filtered_strings)
    
def get_fuel_depth(cat: str, csv_file: str) -> float:
    """ fetch corresponding fuel depth
    """
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['TYPE'] == cat:
                return float(row['FUEL_DEPTH'])
            

def sum_fuel_load(cat: str, csv_file: str) -> float:
    """ use strings to find the sum fuel load for type
        return int calculation
    """
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['TYPE'] == cat:
                sum = float(row['FUEL_LOAD_1']) + float(row['FUEL_LOAD_10']) + float(row['FUEL_LOAD_100'])
                return sum


def sav_average(cat: str, csv_file: str) -> float:
    """ average values for sav if not in 9999 category
    """
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['TYPE'] == cat:
                vals = []
                if float(row['SAV_1HR']) != 9999:
                    vals.append(float(row['SAV_1HR']))
                if float(row['SAV_LIVE']) != 9999:
                    vals.append(float(row['SAV_LIVE']))
                if float(row['SAV_WOODY']) != 9999:
                    vals.append(float(row['SAV_WOODY']))

                assert len(vals) != 0, "fatal; no valid sav found to append"

                return statistics.mean(vals)

def aspect_to_direction(aspect):
    """ use degree to fetch aspect, use for fine dead fuel moisture
    """
    aspect %= 360

    if aspect < 0:
        return "NONE"

    if 315 <= aspect < 45 or (aspect >= 315 and aspect <= 360):
        return 'N'
    elif 45 <= aspect < 135:
        return 'E'
    elif 135 <= aspect < 225:
        return 'S'
    else:
        return 'W'
    
def derive_fuel_moisture(csv_path_table_A: str, 
                         csv_path_correction: str,
                         dry_bulb: float, 
                         relative_humidity: float,
                         aspect: str,
                         slope: int
                         ) -> float:
    """  dead fuel moisture of extinction - fraction

        The dead fuel moisture of
        extinction is the moisture at which the dead fuel will not sustain a spreading surface
        fire; this is a user-supplied value.

        constant value of 0.4 if unable to calculate
    
    """
    try:
        init_ref_val = ref_table_a_moisture(csv_path_table_A, relative_humidity, dry_bulb)
        correction = ref_d_correction(csv_path_correction, aspect, slope)

        return init_ref_val + correction
    except Exception as e:
        print(f"WARNING: failed moisture calculation; subject to default reccommendation from Rothermel documentation. Error: {e}")
        return 0.4

def get_humidity_column(relative_hum):
    """ pattern match to ref table a 
    """
    humidity_ranges = [
        (0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39),
        (40, 44), (45, 49), (50, 54), (55, 59), (60, 64), (65, 69), (70, 74),
        (75, 79), (80, 84), (85, 89), (90, 94), (95, 99), (100, 100)
    ]

    for lower, upper in humidity_ranges:
        if lower <= relative_hum <= upper:
            return f'{lower}_{upper}'

    # for invalid value, throw
    return 'Invalid humidity value'

def ref_table_a_moisture(csv_file, relative_hum, dry_bulb) -> int:
    """ source fuel moisture percentage using rel humidity + bulb temp 
    """

    # map to proper name
    col_rel_humidity = get_humidity_column(relative_hum)

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dry_vals = [int(value) for value in row['DRY_BULB'].split(',')]
            if len(dry_vals) == 1:
                if dry_bulb >= 109:
                    return int(row[col_rel_humidity])
            else:
                num1, num2 = sorted(dry_vals)
                if num1 <= dry_bulb <= num2:
                    return int(row[col_rel_humidity])
                else:
                    continue
            
def convert_to_pacific(utc_time):
    """ convert col names for quick match
    """
    utc_dt = datetime.strptime(utc_time, '%H%M_%H%M')
    utc_offset = timedelta(hours=-8)  # Pacific Time is UTC-8 (standard time)
    pacific_dt = utc_dt + utc_offset

    return pacific_dt.strftime('%H%M_%H%M')
            
def ref_d_correction(csv_file, aspect, slope):
    """ apply fuel moisture correction using aspect + slope + time
    """
    # assume worst case if none sensed
    if aspect == 'NONE':
        aspect = 'S'
    else:
        assert aspect == 'N' or aspect == 'S' or aspect == 'W' or aspect == 'E', "Unidentified aspect provided"

    # PDT fetch 
    utc_offset = timedelta(hours=-7)
    pacific_time = datetime.utcnow() + utc_offset
    cur_pdt_time = pacific_time.strftime('%H%M')

    # fetch val
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Aspect'] == aspect:
                slope_constr = [int(value) for value in row['Slope'].split('_')]
                if len(slope_constr) == 1:
                    num1 = 0
                    num2 = 30
                else:
                    num1 = 31 
                    num2 = 100
                if num1 <= slope <= num2:
                    # slope is matching, proceed to match w time
                    column_names = ['0800_0959', '1000_1159', '1200_1359', '1400_1559', '1600_1759']
                    matching_range = None
                    for name in column_names:
                        start, end = name.split('_')
                        if start <= cur_pdt_time <= end:
                            matching_range = name
                            break

                    if not matching_range:
                        # due to testing, this will auto fail due to local time
                        print("WARNING: time col no matches found, failed search; selecting default 0800")
                        matching_range = '0800_0959'

                    # finally extract val
                    return int(row[matching_range])

def test01_get_simple_fire_spread():
    """ test for get_simple_fire_spread
    """
    fuelload = 0.033976 # lbs/ft^2
    fueldepth = 1 # feet
    windspeed = 5 # mph
    slope = 0 # degrees
    fuelmoisture = 0.05 # as a proportion
    fuelsav = 3500 # 1/ft
    result = get_simple_fire_spread(fuelload, fueldepth, windspeed, slope, fuelmoisture, fuelsav)

    print("Rate of spread (ft/min)", result[0])
    print("Reaction Intensity (Btu/ft/min)", result[1])
    print("Fireline Intensity (Btu/ft)", result[2])
