# %load /home/oliver/Dropbox/whitepine/lib/cron.py
# this file gets run nightly after the rapnet_import script
# any printed output of this script will be sent to Ollie's email, so try not to use print much

###################
##### LOAD ACTIVE LISTINGS FROM SQL DATABASE & DEFINE SOME GLOBAL VARIABLES
###################

import pandas as pd
import numpy as np
import pandas.io.sql as psql
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pylab as pl
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages
import math
import sys
#sys.path.insert(0, '/home/oliver/src/blue-meth/ipynb')
import rapnet_loader as rl
from datetime import datetime
import statsmodels.api as sm
from os import path
import os

def ratio(measurement):
    if pd.isnull(measurement):
        return -999999
    measurementx = (measurement.replace('-','x'))
    dims = (measurementx.split('x'))
    side1 = float(dims[0])
    side2 = float(dims[1])
    if side1 == 0 or side2 == 0:
        return -999999
    else:
        return max(side1/side2, side2/side1)

# cdef = cython function definition
# double - double-precision floating-point number (http://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
# double rap_price_key(double wt) - function that takes a double wt and returns a double
def rap_price_key(wt):
    if wt >= 0.01 and wt <= 0.03:
        return 0.01
    elif wt >= 0.04 and wt <= 0.07:
        return 0.07
    elif wt >= 0.08 and wt <= 0.14:
        return 0.08
    elif wt >= 0.15 and wt <= 0.17:
        return 0.15
    elif wt >= 0.18 and wt <= 0.22:
        return 0.18
    elif wt >= 0.23 and wt <= 0.29:
        return 0.23
    elif wt >= 0.30 and wt <= 0.39:
        return 0.30
    elif wt >= 0.40 and wt <= 0.49:
        return 0.40
    elif wt >= 0.50 and wt <= 0.69:
        return 0.50
    elif 0.70 <= wt and wt <= 0.89:
        return 0.70
    elif 0.90 <= wt and wt <= 0.99:
        return 0.90
    elif 1.00 <= wt and wt <= 1.49:
        return 1.00
    elif 1.50 <= wt and wt <= 1.99:
        return 1.50
    elif 2.00 <= wt and wt <= 2.99:
        return 2.00
    elif 3.00 <= wt and wt <= 3.99:
        return 3.00
    elif 4.00 <= wt and wt <= 4.99:
        return 4.00
    elif 5.00 <= wt and wt <= 9.99:
        return 5.00
    elif 10.00 <= wt:
        return 10.00
    else:
        return -999999.0

def shape_disc_key(wt):
    if wt >= 0.01 and wt <= 0.03:
        return 0.01
    elif wt >= 0.04 and wt <= 0.07:
        return 0.04
    elif wt >= 0.08 and wt <= 0.14:
        return 0.08
    elif wt >= 0.15 and wt <= 0.17:
        return 0.15
    elif wt >= 0.18 and wt <= 0.22:
        return 0.18
    elif wt >= 0.23 and wt <= 0.29:
        return 0.23
    elif wt >= 0.30 and wt <= 0.39:
        return 0.30
    elif wt >= 0.40 and wt <= 0.49:
        return 0.40
    elif wt >= 0.50 and wt <= 0.59:
        return 0.50
    elif wt >= 0.60 and wt <= 0.69:
        return 0.60
    elif 0.70 <= wt and wt <= 0.79:
        return 0.70
    elif 0.80 <= wt and wt <= 0.89:
        return 0.80
    elif 0.90 <= wt and wt <= 0.99:
        return 0.90
    elif 1.00 <= wt and wt <= 1.24:
        return 1.00
    elif 1.25 <= wt and wt <= 1.49:
        return 1.25
    elif 1.50 <= wt and wt <= 1.74:
        return 1.50
    elif 1.75 <= wt and wt <= 1.99:
        return 1.75
    elif 2.00 <= wt and wt <= 2.49:
        return 2.00
    elif 2.50 <= wt and wt <= 2.99:
        return 2.50
    elif 3.00 <= wt and wt <= 3.99:
        return 3.00
    elif 4.00 <= wt and wt <= 4.99:
        return 4.00
    elif 5.00 <= wt and wt <= 9.99:
        return 5.00
    elif 10.00 <= wt:
        return 10.00
    else:
        return -999999.0

def rap_shape_key(shape):
    if shape == 'Round':
        return 'BR'
    else:
        return 'PS'

def discount_shape_key(shape):
    if shape == 'Round':
        return 'RB'
    elif shape == 'Princess':
        return 'PR'
    else:
        return 'NA'

def  depth_diff(depth):
    if depth >= 72.0:
        return depth - 72.0
    elif depth < 64:
        return 64 - depth
    else:
        return 0


def  ratio_diff(ratio):
    return math.fabs(ratio - 1)

def grade_rank(grade):
    if pd.isnull(grade):
        return -999999
    if grade == 'Excellent':
        return 0
    elif grade == 'Very Good':
        return 1
    elif grade == 'Good':
        return 2
    elif grade == 'Fair':
        return 3
    elif grade == 'Poor':
        return 4
    else:
        return -999999    
    
def price_curve_key(wt):
    if wt >= 0.01 and wt <= 0.03:
        return 'r01'
    elif wt >= 0.04 and wt <= 0.07:
        return 'r04'
    elif wt >= 0.08 and wt <= 0.14:
        return 'r08'
    elif wt >= 0.15 and wt <= 0.17:
        return 'r15'
    elif wt >= 0.18 and wt <= 0.22:
        return 'r18'
    elif wt >= 0.23 and wt <= 0.29:
        return 'r23'
    elif wt >= 0.30 and wt <= 0.39:
        return 'r30'
    elif wt >= 0.40 and wt <= 0.49:
        return 'r40'
    elif wt >= 0.50 and wt <= 0.59:
        return 'r50'
    elif 0.60 <= wt and wt <= 0.69:
        return 'r60'
    elif 0.70 <= wt and wt <= 0.79:
        return 'r70'
    elif 0.80 <= wt and wt <= 0.89:
        return 'r80'
    elif 0.90 <= wt and wt <= 0.99:
        return 'r90'
    elif 1.00 <= wt and wt <= 1.49:
        return 'rc1'
    elif 1.50 <= wt and wt <= 1.99:
        return 'rcr'
    elif 2.00 <= wt and wt <= 2.99:
        return 'rc2'
    elif 3.00 <= wt and wt <= 3.99:
        return 'rc3'
    elif 4.00 <= wt and wt <= 4.99:
        return 'rc4'
    elif 5.00 <= wt and wt <= 9.99:
        return 'rc5'
    elif 10.00 <= wt:
        return 'rct'
    else:
        return -999999.0

wp_path = '/home/oliver/Dropbox/whitepine'
all_countries = ['USA', 'Canada', 'United Kingdom', 'Hong Kong', 'India', 'Belgium', 'Israel', 'Sri Lanka', 'Germany', \
            'Thailand', 'UAE', 'China', 'South Africa', 'New Zealand', 'Australia', 'France', 'Singapore', 'Italy', 'Uzbekistan', 'Uganda']
usa_only = ['USA']

colors = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
clars = ['IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'SI3', 'I1', 'I2', 'I3']
colors_plot = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
clars_plot = ['IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1']
coffee_pot_colors = ['F', 'G', 'H', 'I', 'J']
coffee_pot_clars = ['VS1', 'VS2', 'SI1', 'SI2']

fluor_faint = ['Faint ', 'Faint','Faint Blue', 'Slight', 'Very Slight ', 'Slight Blue', 'Very Slight Blue'] #Do NOT delete spaces at end of items in this list
fluor_none = ['None ', 'None'] #Do NOT delete spaces at end of items in this list
fluor_medium = ['Medium','Medium ', 'Medium Blue', 'Medium Yellow'] #Do NOT delete spaces at end of items in this list
fluor_strong = ['Strong','Strong ', 'Strong Blue', 'Very Strong Blue', 'Very Strong '] #Do NOT delete spaces at end of items in this list
fluors = ['Faint ', 'Faint Blue', 'Slight', 'Very Slight ', 'Slight Blue', 'Very Slight Blue', 'None ']
fluor_none_and_faint = ['None','Faint','None ', 'Faint ', 'Faint Blue', 'Slight', 'Very Slight ', 'Slight Blue', 'Very Slight Blue']

clar_line_colors = {'IF' : 'r' , 'VVS1' : 'g', 'VVS2' : 'b', 'VS1' :'c', 'VS2' : 'm', 'SI1': 'y', 'SI2': 'k', 'I1': 'r', 'I2' : 'g'}
color_line_colors = {'D' : 'r' , 'E' : 'g', 'F' : 'b', 'G' :'c', 'H' : 'm', 'I' : 'y', 'J': 'k', 'K': 'r', 'L' : 'g', 'M' : 'b'}

# grade all princess cuts
def set_grade(df, df_p, mindepth, maxdepth, maxratio, sym, polish, grade):
    df_i = df_p[(df_p.Depth >= mindepth) 
               & (df_p.Depth <= maxdepth) 
               & (df_p.Ratio <= maxratio)
               & (df_p.Sym.isin(sym))
               & (df_p.Polish.isin(polish))
               ]
    df.loc[df_i.index, 'Cut Grade'] = grade

###################
##### FITS POLYNOMIALS TO TOTAL PRICE DATA (X = CARAT WEIGHT, Y = TOTAL PRICE) AND EXPORTS THE FIT PARAMETERS TO EXCEL
###################

def price_curve_generator_all(df, wp_path, file_date):
    output = {\
                'Shape' : [], \
                'Color' : [], \
                'Clarity' : [], \
                'CurveKey' : [], \
                'CurveRangeMin' : [], \
                'CurveRangeMax' : [], \
                'PolyDegree' : [], \
                'Px2' : [], \
                'Px1' : [], \
                'Px0' : [], \
                'StdDev' : [], \
                'NumStones': [], \
                'ResidSlope': [], \
                'ResidCept': [] \
                }
    r01 = np.linspace(0.00, 0.03, 50)
    r04 = np.linspace(0.04, 0.07, 50)
    r08 = np.linspace(0.08, 0.14, 50)
    r15 = np.linspace(0.15, 0.17, 50)
    r18 = np.linspace(0.18, 0.22, 50)
    r23 = np.linspace(0.23, 0.29, 50)
    r30 = np.linspace(0.30, 0.39, 50)
    r40 = np.linspace(0.40, 0.49, 50)
    r50 = np.linspace(0.50, 0.59, 50)
    r60 = np.linspace(0.60, 0.69, 50)
    r70 = np.linspace(0.70, 0.79, 50)
    r80 = np.linspace(0.80, 0.89, 50)
    r90 = np.linspace(0.90, 0.99, 50)
    rc1 = np.linspace(1.00, 1.49, 50)
    rcr = np.linspace(1.50, 1.99, 50)
    rc2 = np.linspace(2.00, 2.99, 50)
    rc3 = np.linspace(3.00, 3.99, 50)
    rc4 = np.linspace(4.00, 4.99, 50)
    rc5 = np.linspace(5.00, 9.99, 50)
    rct = np.linspace(10.00, 29.99, 50)

    rc_bins = [r01, r04, r08, r15, r18, r23, r30, r40, r50, r60, r70, r80, r90, rc1, rcr, rc2, rc3, rc4, rc5, rct]


    shapes = [ \
                ['Princess', ['Excellent'],  ['Excellent', 'Very Good', 'Good'],  ['Excellent', 'Very Good', 'Good'], 'PS', usa_only, 'PR'], \
                ['Round', ['Excellent'],  ['Excellent'],  ['Excellent'], 'BR', all_countries, 'RB'] \
                ]

    #initiate pdf doc to save figures into
    pp = PdfPages(path.join(wp_path, 'price_curves_optimized_{0}.pdf'.format(file_date)))

    df_caratfilt = df[(df.Carat >= 0.23) & (df.Carat < 3.50) & (df.Price > 0)]
    for z in range(len(shapes)):
        shape = shapes[z][0]
        cutgrade = shapes[z][1]
        polish = shapes[z][2]
        sym = shapes[z][3]
        rap_shape_key = shapes[z][4]
        location = shapes[z][5]
        shape_key = shapes[z][6]

        # hoist common comparisons out of the loops so we only do them once per shape
        df_iter = df_caratfilt[(df_caratfilt.Country.isin(location)) 
                               & (df_caratfilt['Cut Grade'].isin(cutgrade))
                               & (df_caratfilt.Polish.isin(polish))
                               & (df_caratfilt.Sym.isin(sym))
                               & (df_caratfilt.Fluor.isin(fluor_none))
                              ]
        carat_bins = [ \
                  (0.00, 0.04, 0.01, 0.03, 0.01, 1, 'r01', r01),\
                  (0.04, 0.08, 0.04, 0.07, 0.04, 1, 'r04', r04),\
                  (0.08, 0.15, 0.08, 0.14, 0.08, 1, 'r08', r08),\
                  (0.15, 0.18, 0.15, 0.17, 0.15, 1, 'r15', r15),\
                  (0.18, 0.23, 0.18, 0.22, 0.18, 1, 'r18', r18),\
                  (0.23, 0.30, 0.23, 0.29, 0.23, 1, 'r23', r23),\
                  (0.30, 0.40, 0.30, 0.39, 0.30, 1, 'r30', r30),\
                  (0.40, 0.50, 0.40, 0.49, 0.40, 1, 'r40', r40),\
                  (0.50, 0.60, 0.50, 0.59, 0.50, 1, 'r50', r50),\
                  (0.60, 0.70, 0.60, 0.69, 0.50, 1, 'r60', r60),\
                  (0.70, 0.80, 0.70, 0.79, 0.70, 1, 'r70', r70),\
                  (0.80, 0.90, 0.80, 0.89, 0.70, 1, 'r80', r80),\
                  (0.90, 1.00, 0.90, 0.99, 0.90, 1, 'r90', r90),\
                  (1.00, 1.50, 1.00, 1.49, 1.00, 2, 'rc1', rc1),\
                  (1.50, 2.00, 1.50, 1.99, 1.50, 2, 'rcr', rcr),\
                  (2.00, 3.00, 2.00, 2.99, 2.00, 2, 'rc2', rc2),\
                  (3.00, 4.00, 3.00, 3.99, 3.00, 2, 'rc3', rc3),\
                  (4.00, 5.00, 4.00, 4.99, 4.00, 2, 'rc4', rc4),\
                  (5.00, 10.00, 5.00, 9.99, 5.00, 2, 'rc5', rc5),\
                  (10.00, 30.00, 10.00, 29.99, 10.00, 2, 'rct', rct)\
                  ]
        line_colors = ['r', 'g', 'b', 'c', 'm', 'y', 
                'k', 'r', 'g', 'b', 'c', 'm', 'y', 'k', 
                'r', 'g', 'b', 'c', 'm', 'y']
        for i in range(len(carat_bins)):
            fxn_min = carat_bins[i][0]
            fxn_max = carat_bins[i][1]
            plot_min = carat_bins[i][2]
            plot_max = carat_bins[i][3]
            rap_price_key = carat_bins[i][4]
            degree = carat_bins[i][5]
            curve_key = carat_bins[i][6]
            plot_linspace = carat_bins[i][7]
            fxn_plus_min = fxn_max # carat_bins[i][1]
            fxn_plus_max = fxn_plus_min + .5 #carat_bins[i][1]+.5


            for color in colors_plot:
                for clar in clars_plot:
                    #create a smaller dataframe with a single combination of color and clarity
                    df_temp = df_iter[ \
                                (df_iter['Shape'] == shape) \
                                & (df_iter['Color'] == color) \
                                & (df_iter['Clarity'] == clar) \
                                ]

                    #break up color/clarity dataframe into smaller chunks based on carat weight
                    df_fxn_range_pre = df_temp[(df_temp['Carat'] >= fxn_min) & (df_temp['Carat'] < fxn_max)]
                    df_fxn_range_plus_pre = df_temp[(df_temp['Carat'] >= fxn_plus_min) & (df_temp['Carat'] < fxn_plus_max)]

                    #get cheapest two stones that weigh more than the current weight bin, append them to the smaller color/clarity dataframe
                    cheapest_n = lambda d, n: d.loc[d.TotalPrice.nsmallest(n).index]
                    if degree == 2:
                        df_fxn_range = pd.concat([df_fxn_range_pre, cheapest_n(df_fxn_range_plus_pre, 2)])
                    elif degree == 1:
                        df_fxn_range = pd.concat([df_fxn_range_pre, cheapest_n(df_fxn_range_plus_pre, 1)])
                    else:
                        df_fxn_range = []
                    #df_fxn_range = pd.concat([df_fxn_range_pre, df_fxn_range_plus[:2]])
                    df_plot_range = df_temp[(df_temp['Carat'] >= plot_min) & (df_temp['Carat'] < plot_max)]


                    #exception handling for certain criteria... exclude small and large stones, exclude lesser clarities, exclude empty categories
                    #exclude categories with only a few stones (minimum stone limits set here are arbitrary)
                    #create dummy entries in the output dictionary for the exlcluded categories
                    if ( \
                        plot_min < .3 \
                        or (plot_min < .5 and shape == 'Princess')
                        or plot_max >= 3.00 \
                        or clar == 'SI3' \
                        or clar == 'I2' \
                        or clar == 'I3' \
                        or len(df_temp) == 0 \
                        or (len(df_fxn_range_pre) <= 4 and degree ==1) \
                        or (len(df_fxn_range) <= 9 and degree ==2) \
                        or len(df_fxn_range) == 0
                        or len(df_plot_range) == 0
                        ):

                        output['Shape'].append(shape_key)
                        output['Color'].append(color)
                        output['Clarity'].append(clar)
                        output['CurveKey'].append(curve_key)
                        output['CurveRangeMin'].append(plot_min)
                        output['CurveRangeMax'].append(plot_max)
                        output['PolyDegree'].append(-999999)
                        output['Px2'].append(-999999)
                        output['Px1'].append(-999999)
                        output['Px0'].append(-999999)
                        output['StdDev'].append(-999999)
                        output['NumStones'].append(len(df_plot_range))
                        output['ResidSlope'].append(-999999)
                        output['ResidCept'].append(-999999)

                    else:
                        #calculate fit parameters for best fit polynomial curve
                        fit_params = np.poly1d(np.polyfit(df_fxn_range['Carat'],df_fxn_range['TotalPrice'], degree, full=False))

                        #Calculate the standard deviation of list prices versus model projected prices in terms of pct rap (i.e., % difference of model price and listed price from rap list price)
                        total = np.sum(((np.polyval(fit_params, df_plot_range['Carat'])
                                            - df_plot_range['TotalPrice']) 
                                        / (np.polyval(fit_params, df_plot_range['Carat']))) ** 2)

                        curve_shift = math.sqrt(total / len(df_plot_range))

                        #Calculate a residual value - the % difference between predicted price and list price
                        s_residual = (df_plot_range['TotalPrice']-np.polyval(fit_params, df_plot_range['Carat']))/df_plot_range['TotalPrice']
                        df.loc[df_plot_range.index, 'Residual'] = s_residual

                        resid_slope = np.poly1d(np.polyfit(df_plot_range['Carat'],s_residual, 1, full=False))

                        #Store fit parameters in a dictionary
                        if degree == 1:
                            output['Shape'].append(shape_key)
                            output['Color'].append(color)
                            output['Clarity'].append(clar)
                            output['CurveKey'].append(curve_key)
                            output['CurveRangeMin'].append(plot_min)
                            output['CurveRangeMax'].append(plot_max)
                            output['PolyDegree'].append(degree)
                            output['Px2'].append(0)
                            output['Px1'].append(fit_params[1])
                            output['Px0'].append(fit_params[0])
                            output['StdDev'].append(curve_shift)
                            output['NumStones'].append(len(df_plot_range))
                            output['ResidSlope'].append(resid_slope[1]*(fxn_max-fxn_min))
                            output['ResidCept'].append(resid_slope[0])
                        elif degree == 2:
                            output['Shape'].append(shape_key)
                            output['Color'].append(color)
                            output['Clarity'].append(clar)
                            output['CurveKey'].append(curve_key)
                            output['CurveRangeMin'].append(plot_min)
                            output['CurveRangeMax'].append(plot_max)
                            output['PolyDegree'].append(degree)
                            output['Px2'].append(fit_params[2])
                            output['Px1'].append(fit_params[1])
                            output['Px0'].append(fit_params[0])
                            output['StdDev'].append(curve_shift)
                            output['NumStones'].append(len(df_plot_range))
                            output['ResidSlope'].append(resid_slope[1]*(fxn_max-fxn_min))
                            output['ResidCept'].append(resid_slope[0])
                        else:
                            output['Shape'].append(shape_key)
                            output['Color'].append(color)
                            output['Clarity'].append(clar)
                            output['CurveKey'].append(curve_key)
                            output['CurveRangeMin'].append(plot_min)
                            output['CurveRangeMax'].append(plot_max)
                            output['PolyDegree'].append(-999999)
                            output['Px2'].append(-999999)
                            output['Px1'].append(-999999)
                            output['Px0'].append(-999999)
                            output['StdDev'].append(-999999)
                            output['NumStones'].append(len(df_plot_range))
                            output['ResidSlope'].append(-999999)
                            output['ResidCept'].append(-999999)

                        #load rap price for color/clarity/weight combination
                        #rap_price = df_rap_price_list['PricePerCar'].ix[rap_shape_key].ix[color].ix[clar].ix[rap_price_key]

                        ###plot best fit curves, best fit curve less the stdev calc, & scatter of price v weight

                        #DEACTIVATED
                        plt.subplot(2,1,1)
                        plt.plot(rc_bins[i], np.polyval(fit_params, plot_linspace), color = line_colors[i])
                        plt.plot(rc_bins[i], (np.polyval(fit_params, plot_linspace) - np.polyval(fit_params, plot_linspace)*curve_shift), '--', color=line_colors[i])
                        plt.scatter(df_plot_range['Carat'], df_plot_range['TotalPrice'], color=line_colors[i], alpha=.7)

                        #calculate a curve that will display on the residual chart showing the difference between the model price and the price of a stone 1 stdev away from the model price
                        curve_shift_resid = -(np.polyval(fit_params, plot_linspace) - np.polyval(fit_params, plot_linspace)*(1-curve_shift))/np.polyval(fit_params, plot_linspace)

                        #plot residuals
                        plt.subplot(2,1,2)
                        plt.plot(plot_linspace, curve_shift_resid, '--', color=line_colors[i])
                        plt.scatter(df_plot_range['Carat'],s_residual,color=line_colors[i],alpha=.7)
                        plt.axhline(linewidth=1, color='k')


                #set plot limits - exception handling for empty dataframes

                if len(df_temp) == 0:
                    ymin = 0
                    ymax = 10000
                else:
                    ymin = df_temp['TotalPrice'].min()*0.95
                    ymax = df_temp['TotalPrice'].max()*1.05

                #label and format plots
                #plt.rcParams['figure.figsize'] = 9, 9
                if clar in ['SI3', 'I2', 'I3']:
                    pass
                else:
                    plt.rcParams['figure.figsize'] = 9, 9
                    #plt.subplot(2,1,1)
                    plt.title(shape+'- 0.30 - 2.99 carat - '+color+' - '+clar, fontsize = 16)
                    plt.ylabel('Total Price of Stone', fontsize = 16)
                    plt.ylim(ymin, ymax)
                    #plt.ylim(0,10000)
                    plt.annotate("N = %s stones" %(len(df_temp)), xy=(1, 0), xycoords='axes fraction', fontsize=16, xytext=(-5, 5), textcoords='offset points', ha='right', va='bottom')
                    plt.xlim(0.23,3.00)

                    plt.subplot(2,1,2)
                    plt.title('Residuals', fontsize = 16)
                    plt.ylabel('% Diff Btwn Actual and Model Price', fontsize = 16)
                    plt.xlabel('Carat Weight', fontsize = 16)
                    plt.ylim(-.5,.5)
                    plt.xlim(0.23,3.00)

                plt.savefig(pp, format='pdf') #save figure to pdf
                plt.clf() #clear the figure for next iteration

    pp.close() #close pdf

    #create a dataframe that contains the curve fit parameters
#    arrays = [output['Shape'], output['Color'], output['Clarity'], output['CurveKey'], output['CurveRangeMin']]
#    tuples = zip(*arrays)
#    index = pd.MultiIndex.from_tuples(tuples)
    shape = output['Shape']
    color = output['Color']
    clarity = output['Clarity']
    curvekey = output['CurveKey']
    assert(all([len(shape), len(color), len(clarity), len(curvekey)]))
    columns = ['Shape','Color','Clarity','CurveKey','CurveRangeMin','PolyDegree','Px2','Px1','Px0','StdDev','NumStones', 'ResidSlope', 'ResidCept']
    output2 = { 'Shape' : shape,
                'Color' : color,
                'Clarity' : clarity,
                'CurveKey' : curvekey,
                'CurveRangeMin' : output['CurveRangeMin'],
                'CurveRangeMax' : output['CurveRangeMax'], \
                'PolyDegree' : output['PolyDegree'], \
                'Px2': output['Px2'], \
                'Px1': output['Px1'], \
                'Px0' : output['Px0'], \
                'StdDev': output['StdDev'], \
                'NumStones': output['NumStones'], \
                'ResidSlope': output['ResidSlope'], \
                'ResidCept': output['ResidCept'] \
                }

    df_output = pd.DataFrame(output2,
                     index=['{0}_{1}_{2}_{3}'.format(s,co,cl,cu) 
                                   for s,co,cl,cu in zip(shape, color, clarity, curvekey)
                                  ],
                     columns = ['Shape','Color','Clarity','CurveKey','CurveRangeMin','PolyDegree', 'Px2', 'Px1', 'Px0', 'StdDev', 'NumStones', 'ResidSlope', 'ResidCept'] 
                     )

    #df_output.to_excel('/home/oliver/Dropbox/whitepine/price_curve_params.csv')
    df_sel = df_output[((df_output.PolyDegree == 1) & (df_output.Px1 < 0))
                            | ((df_output.PolyDegree == 2) & (df_output.Px1 > 80000))]
    df_output.loc[df_sel.index, 'Px2'] = -999999
    df_output.loc[df_sel.index, 'Px1'] = -999999
    df_output.loc[df_sel.index, 'Px0'] = -999999
    df_output.loc[df_sel.index, 'StdDev'] = -999999

    return df_output


def create_shape_discs(df):
    output_df = df[df['Fluor'].isin(fluor_none_and_faint)].groupby(['Shape', 'Color', 'Clarity', 'ShapeDiscKey']).agg({"PctRap":np.mean, "Residual":len})
    #df_flatkey.reindex(df_flatkey.index.map(idx: "_".join(idx)), columns = ["Len"])
    #idx = df_flatkey.df_flatkey.reset_index().reindex()
    idx = output_df.index.map(lambda idx: "{}_{}_{}_{}".format(idx[1],idx[2],idx[3],idx[0]))
    output_df = output_df.reset_index()
    output_df.index = idx
    output_df.columns = ['Shape','Color','Clarity','Min Wght','Avg Discount','Num Stones']
    return output_df

def write_excel(df, wp_path, file_date, df_rap_price_list):
    file_name = path.join(wp_path, 'prdt_optimized_{0}.xlsx'.format(file_date))
    df_price_curves = price_curve_generator_all(df, wp_path, file_date)
    writer = pd.ExcelWriter(file_name)
    df_price_curves.to_excel(writer, 'PRICE PARAMS')

    create_shape_discs(df).to_excel(writer, 'SHAPE DISCS')

    df['PriceCurveKey'] = df['Carat'].apply(price_curve_key)
    df_index_cols = ['DiscountShapeKey','Color','Clarity','PriceCurveKey']
    px_curve_index_cols = ['Shape','Color','Clarity','CurveKey']
    px_curve_cols = ['PolyDegree','Px2','Px1','Px0','StdDev']
    df = pd.merge(df, df_price_curves[px_curve_index_cols+px_curve_cols], how="left", 
             left_on  = df_index_cols,
             right_on = px_curve_index_cols,
             suffixes = ['','_c']
            )

    df['PredictedPrice'] = df['Carat']**2 * df['Px2'] +  df['Carat'] * df['Px1'] + df['Px0']
    df['PredictedPricePerCarat'] = df['PredictedPrice'] / df['Carat']
    df['PredictedPctRap'] = (df['PredictedPricePerCarat'] - df['RapPricePerCarat']) / df['RapPricePerCarat']
    df['PredictedPercentDiff'] = (df['TotalPrice']-df['PredictedPrice'])/df['PredictedPrice']

    clars = ['IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'SI3', 'I1', 'I2','I3','Blank_Col']
    def get_clars(suffix):
        return [c + suffix for c in clars]

    clars_avg = get_clars("_avg")
    clars_med = get_clars("_med")
    clars_std = get_clars("_std")
    clars_num = get_clars("_num")[:-1]
    clars_blnk = get_clars("")

    clars_tot = clars_avg + clars_med + clars_std + clars_num

    usa_only = ['USA']

    discount_groups = [ [['D'], ['IF', 'VVS1', 'VVS2']], \
                        [['E', 'F'], ['IF', 'VVS1', 'VVS2']], \
                        [['G', 'H', 'I', 'J'], ['IF', 'VVS1', 'VVS2']], \
                        [['D'], ['VS1', 'VS2', 'SI1', 'SI2']], \
                        #[['E', 'F', 'G', 'H', 'I', 'J'], ['VS1', 'VS2']], \
                        #[['E', 'F', 'G', 'H', 'I', 'J'], ['SI1', 'SI2']], \
                        [['E', 'F'], ['VS1', 'VS2']], \
                        [['G', 'H', 'I', 'J'], ['VS1', 'VS2']], \
                        [['E', 'F'], ['SI1', 'SI2']], \
                        [['G', 'H', 'I', 'J'], ['SI1', 'SI2']], \
                        [['K', 'L'], ['IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2']]\
                        ]

    ex = ['Excellent']
    vg = ['Very Good']
    gd = ['Good']
    fr = ['Fair']

    vg_plus = ['Excellent', 'Very Good']
    gd_plus = ['Excellent', 'Very Good', 'Good']
    fr_plus = ['Excellent', 'Very Good', 'Good', 'Fair']
    tot = ['Excellent', 'Very Good', 'Good', 'Fair']

    # TAG , CUT , polish, sym, fluor

    discounts = [ \
                ['EX_EX_EX_NO_CPBOOST', ex, ex, ex, fluor_none, usa_only, 'Round', 'RB'], \
                ['EX_EX_EX_NO', ex, ex, ex, fluor_none, all_countries, 'Round', 'RB'], \
                ['EX_EX_EX_FNT', ex, ex, ex, fluor_faint, all_countries, 'Round', 'RB'], \
                ['EX_EX_EX_MED', ex, ex, ex, fluor_medium, all_countries, 'Round', 'RB'], \
                ['EX_EX_EX_STRONG', ex, ex, ex, fluor_strong, all_countries, 'Round', 'RB'], \
                ['VG_VGPLUS_VGPLUS_NO', vg, vg_plus, vg_plus, fluor_none, all_countries, 'Round', 'RB'], \
                ['VG_VGPLUS_VGPLUS_FNT', vg, vg_plus, vg_plus, fluor_faint, all_countries, 'Round', 'RB'], \
                ['VG_VGPLUS_VGPLUS_MED', vg, vg_plus, vg_plus, fluor_medium, all_countries, 'Round', 'RB'], \
                ['VG_VGPLUS_VGPLUS_STRONG', vg, vg_plus, vg_plus, fluor_strong, all_countries, 'Round', 'RB'], \
                ['GD_GDPLUS_GDPLUS_NO', gd, gd_plus, gd_plus, fluor_none, all_countries, 'Round', 'RB'], \
                ['GD_GDPLUS_GDPLUS_FNT', gd, gd_plus, gd_plus, fluor_faint, all_countries, 'Round', 'RB'], \
                ['GD_GDPLUS_GDPLUS_MED', gd, gd_plus, gd_plus, fluor_medium, all_countries, 'Round', 'RB'], \
                ['GD_GDPLUS_GDPLUS_STRONG', gd, gd_plus, gd_plus, fluor_strong, all_countries, 'Round', 'RB'], \
                ['FR_FRPLUS_FRPLUS_NO', fr, fr_plus, fr_plus, fluor_none, all_countries, 'Round', 'RB'], \
                ['FR_FRPLUS_FRPLUS_FNT', fr, fr_plus, fr_plus, fluor_faint, all_countries, 'Round', 'RB'], \
                ['FR_VGPLUS_FRPLUS_MED', fr, fr_plus, fr_plus, fluor_medium, all_countries, 'Round', 'RB'], \
                ['FR_FRPLUS_FRPLUS_STRONG', fr, fr_plus, fr_plus, fluor_strong, all_countries, 'Round', 'RB'], \
                ['ANY_GDPLUS_GD_NO', ["Good", "Very Good"], gd_plus, gd_plus, fluor_none, usa_only, 'Princess', 'PR'], \
                ]

    discount_bins = [ \
                     [0.23, 1.00], \
                     [1.00, 1.50], \
                     [1.50, 2.99], \
                     ]

    df['PredictedPrice'] = df['Carat']**2 * df['Px2'] +  df['Carat'] * df['Px1'] + df['Px0']
    df['PredictedPricePerCarat'] = df['PredictedPrice'] / df['Carat']
    df['PredictedPctRap'] = (df['PredictedPricePerCarat'] - df['RapPricePerCarat']) / df['RapPricePerCarat']

    discount_output = { 'Tag' : [], 'RB Avg Discount': [], 'RB Median Discount' : [], 'RB Discount Stdev' : [], 'Num Stones' : [], \
                             'PR DepthDiff Coefficient' : [], 'PR Sym Rank Coefficient' : [], \
                             'PR DepthDiff T-Stat' : [], 'PR Sym Rank T-Stat' : []}

    # exclude invalid prices
    df_valid_px = df[df.Px2 != -999999]

    for p in range(len(discount_bins)):
        min_carat = discount_bins[p][0]
        max_carat = discount_bins[p][1]
        df_bin = df_valid_px[(df.Carat >= min_carat) & (df.Carat < max_carat)]
        for i in range(len(discounts)):
            df_avg_discount = pd.DataFrame(0, index=colors, columns=clars_blnk, dtype=np.float64)
            df_med_discount = pd.DataFrame(0, index=colors, columns=clars_blnk, dtype=np.float64)
            df_std_discount = pd.DataFrame(0, index=colors, columns=clars_blnk, dtype=np.float64)
            df_number_of_stones = pd.DataFrame(0, index=colors, columns=clars, dtype=np.float64)

            tag = discounts[i][0]
            cut = discounts[i][1]
            polish = discounts[i][2]
            sym = discounts[i][3]
            fluor = discounts[i][4]
            location = discounts[i][5]
            shape = discounts[i][6]
            shape_tag = discounts[i][7]

            df_discount = df_bin[ \
                (df_bin['Shape'] == shape)
                & (df_bin['Country'].isin(location)) \
                & (df_bin['Cut Grade'].isin(cut)) \
                & (df_bin['Polish'].isin(polish)) \
                & (df_bin['Sym'].isin(sym)) \
                & (df_bin['Fluor'].isin(fluor)) \
                ] #

            for m in range(len(discount_groups)):
                color = discount_groups[m][0]
                clar = discount_groups[m][1]

                df_temp = df_discount[(df_discount['Color'].isin(color)) & (df_discount['Clarity'].isin(clar))]

                avg_discount = np.mean(df_temp['ExactPctRap'] - df_temp['PredictedPctRap'])
                med_discount = np.median(df_temp['ExactPctRap'] - df_temp['PredictedPctRap'])
                std_discount = np.std(df_temp['ExactPctRap'] - df_temp['PredictedPctRap'])
                num_stones = len(df_temp)

                if shape == 'Round':
                    if len(df_temp) == 0:
                        for j in discount_groups[m][0]:
                            for k in discount_groups[m][1]:
                                df_number_of_stones.ix[j,k] = 0
                                df_avg_discount.ix[j,k] = -999999
                                df_med_discount.ix[j,k] = -999999
                                df_std_discount.ix[j,k] = -999999
                                discount_output['Tag'].append("%s_%sct_%sct_%s_%s_%s" %(shape_tag,min_carat,max_carat,j,k,tag))
                                discount_output['RB Avg Discount'].append(-999999)
                                discount_output['RB Median Discount'].append(-999999)
                                discount_output['RB Discount Stdev'].append(-999999)
                                discount_output['Num Stones'].append(0)
                                #discount_output['PR Intercept Coefficient'].append(-999999)
                                discount_output['PR DepthDiff Coefficient'].append(-999999)
                                discount_output['PR Sym Rank Coefficient'].append(-999999)
                                #discount_output['PR Intercept T-Stat'].append(-999999)
                                discount_output['PR DepthDiff T-Stat'].append(-999999)
                                discount_output['PR Sym Rank T-Stat'].append(-999999)

                    elif len(df_temp) <= 7:
                        for j in discount_groups[m][0]:
                            for k in discount_groups[m][1]:
                                df_number_of_stones.ix[j,k] = len(df_temp)
                                df_avg_discount.ix[j,k] = -999999
                                df_med_discount.ix[j,k] = -999999
                                df_std_discount.ix[j,k] = -999999
                                discount_output['Tag'].append("%s_%sct_%sct_%s_%s_%s" %(shape_tag,min_carat,max_carat,j,k,tag))
                                discount_output['RB Avg Discount'].append(-999999)
                                discount_output['RB Median Discount'].append(-999999)
                                discount_output['RB Discount Stdev'].append(-999999)
                                discount_output['Num Stones'].append(len(df_temp))
                                #discount_output['PR Intercept Coefficient'].append(-999999)
                                discount_output['PR DepthDiff Coefficient'].append(-999999)
                                discount_output['PR Sym Rank Coefficient'].append(-999999)
                                #discount_output['PR Intercept T-Stat'].append(-999999)
                                discount_output['PR DepthDiff T-Stat'].append(-999999)
                                discount_output['PR Sym Rank T-Stat'].append(-999999)

                    else:
                        for j in discount_groups[m][0]:
                            for k in discount_groups[m][1]:
                                df_number_of_stones.ix[j,k] = num_stones
                                df_avg_discount.ix[j,k] = avg_discount
                                df_med_discount.ix[j,k] = med_discount
                                df_std_discount.ix[j,k] = std_discount
                                discount_output['Tag'].append("%s_%sct_%sct_%s_%s_%s" %(shape_tag,min_carat,max_carat,j,k,tag))
                                discount_output['RB Avg Discount'].append(avg_discount)
                                discount_output['RB Median Discount'].append(med_discount)
                                discount_output['RB Discount Stdev'].append(std_discount)
                                discount_output['Num Stones'].append(len(df_temp))
                                #discount_output['PR Intercept Coefficient'].append(-999999)
                                discount_output['PR DepthDiff Coefficient'].append(-999999)
                                discount_output['PR Sym Rank Coefficient'].append(-999999)
                                #discount_output['PR Intercept T-Stat'].append(-999999)
                                discount_output['PR DepthDiff T-Stat'].append(-999999)
                                discount_output['PR Sym Rank T-Stat'].append(-999999)

                elif shape == 'Princess':
                    if len(df_temp) == 0:
                        for j in discount_groups[m][0]:
                            for k in discount_groups[m][1]:
                                df_number_of_stones.ix[j,k] = 0
                                discount_output['Tag'].append("%s_%sct_%sct_%s_%s_%s" %(shape_tag,min_carat,max_carat,j,k,tag))
                                discount_output['RB Avg Discount'].append(-999999)
                                discount_output['RB Median Discount'].append(-999999)
                                discount_output['RB Discount Stdev'].append(-999999)
                                #discount_output['PR Intercept Coefficient'].append(-999999)
                                discount_output['PR DepthDiff Coefficient'].append(-999999)
                                discount_output['PR Sym Rank Coefficient'].append(-999999)
                                discount_output['Num Stones'].append(0)
                                #discount_output['PR Intercept T-Stat'].append(-999999)
                                discount_output['PR DepthDiff T-Stat'].append(-999999)
                                discount_output['PR Sym Rank T-Stat'].append(-999999)

                    elif len(df_temp) <= 12:
                        for j in discount_groups[m][0]:
                            for k in discount_groups[m][1]:
                                df_number_of_stones.ix[j,k] = len(df_temp)
                                discount_output['Tag'].append("%s_%sct_%sct_%s_%s_%s" %(shape_tag,min_carat,max_carat,j,k,tag))
                                discount_output['RB Avg Discount'].append(-999999)
                                discount_output['RB Median Discount'].append(-999999)
                                discount_output['RB Discount Stdev'].append(-999999)
                                #discount_output['PR Intercept Coefficient'].append(-999999)
                                discount_output['PR DepthDiff Coefficient'].append(-999999)
                                discount_output['PR Sym Rank Coefficient'].append(-999999)
                                discount_output['Num Stones'].append(len(df_temp))
                                #discount_output['PR Intercept T-Stat'].append(-999999)
                                discount_output['PR DepthDiff T-Stat'].append(-999999)
                                discount_output['PR Sym Rank T-Stat'].append(-999999)

                    else:
                        df_regress_temp = df_temp[(df_temp['PredictedPercentDiff'] <= 0.1) & (df_temp['Carat'] >= .4)]
                        df_princess_regression = pd.DataFrame([df_regress_temp['PredictedPercentDiff'],df_regress_temp['DepthDiff'],df_regress_temp['SymRank']]).transpose()

                        y = df_princess_regression['PredictedPercentDiff']
                        X = sm.add_constant(df_princess_regression.drop(['PredictedPercentDiff'], axis = 1))
                        model = sm.OLS(y, X)
                        reg_results = model.fit()

                        for j in discount_groups[m][0]:
                            for k in discount_groups[m][1]:
                                df_number_of_stones.ix[j,k] = len(df_temp)
                                discount_output['Tag'].append("%s_%sct_%sct_%s_%s_%s" %(shape_tag,min_carat,max_carat,j,k,tag))
                                discount_output['RB Avg Discount'].append(-999999)
                                discount_output['RB Median Discount'].append(-999999)
                                discount_output['RB Discount Stdev'].append(-999999)
                                #discount_output['PR Intercept Coefficient'].append(reg_results.beta['intercept'])
                                discount_output['PR DepthDiff Coefficient'].append(reg_results.params[0]) # 'params' are betas for OLS
                                discount_output['PR Sym Rank Coefficient'].append(reg_results.params[1])
                                discount_output['Num Stones'].append(len(df_temp))
                                #discount_output['PR Intercept T-Stat'].append(reg_results.t_stat['intercept'])
                                discount_output['PR DepthDiff T-Stat'].append(reg_results.tvalues[0])
                                discount_output['PR Sym Rank T-Stat'].append(reg_results.tvalues[1])
    arrays = [discount_output['Tag']]
    tuples = zip(*arrays)
    index = pd.MultiIndex.from_tuples(tuples)

    df_discount_output = pd.DataFrame(discount_output, index=index,  columns=['RB Avg Discount', 'RB Median Discount', 'RB Discount Stdev', \
                             'PR DepthDiff Coefficient', 'PR Sym Rank Coefficient', \
                             'PR DepthDiff T-Stat', 'PR Sym Rank T-Stat', 'Num Stones'])

    df_discount_output.to_excel(writer, 'DISCOUNTS LIST')
    temp = df_rap_price_list #.reset_index()
    temp.columns = ['Shape','Clarity','Color','Min Wght','Max Wght','Price','Date']
    temp['Idx'] = temp.apply(lambda x: '%s_%s_%s_%s' %(x['Shape'], x['Color'], x['Clarity'], x['Min Wght']), axis=1)
    temp = temp.set_index(['Idx'])
    temp.to_excel(writer, 'RAP PRICE LIST')
    pd.DataFrame({'Date': [file_date]}).to_excel(writer, 'sheet1')
    writer.save()

def load_data(file_date):
    #all_df, current_df, file_date = rl.load_cache()
    d = datetime.strptime(file_date, "%Y%m%d")
    current_df = rl.read_daily_file(d)
    csv_path = path.join(wp_path, 'Rapnet Price List {0}.csv'.format(file_date))
    if not path.isfile(csv_path):
        csv_path = path.join(wp_path, 'Rapnet Price List.csv')
    #import rappaport price list
    df_rap_price_list =  pd.read_csv(csv_path, sep=',', header=0,\
        names = ['Shape','Clarity','Color','MinCarat','MaxCarat','PricePerCar','Date'])
    df = current_df[current_df.Cert == 'GIA'].copy()
    df['TotalPrice'] = df['Price'] * df['Carat'] #l.Price represents price per carat
    df['RapPriceKey'] = df['Carat'].apply(rap_price_key)
    df['RapShapeKey'] = df['Shape'].apply(rap_shape_key)
    df['ShapeDiscKey'] = df['Carat'].apply(shape_disc_key)
    df['DiscountShapeKey'] = df['Shape'].apply(discount_shape_key)
    df = pd.merge(df, df_rap_price_list, how = 'left', left_on = ['RapShapeKey','Color','Clarity','RapPriceKey'],
                   right_on = ['Shape','Color','Clarity','MinCarat'], suffixes = ['','_pl'])
    df.rename(columns={'PricePerCar':'RapPricePerCarat'}, inplace=True)
    df.loc[df[df.RapPricePerCarat.isnull()].index, 'RapPricePerCarat'] = -999999
    df['ExactPctRap'] = (df['Price'] - df['RapPricePerCarat']) / df['RapPricePerCarat']
    df['Ratio'] = df['Meas'].apply(ratio)
    df['DepthDiff'] = df['Depth'].apply(depth_diff)
    df['RatioDiff'] = df['Ratio'].apply(ratio_diff)
    df['SymRank'] = df['Sym'].apply(grade_rank)

    df_p = df[df.Shape == 'Princess']
    set_grade(df, df_p, 56, 82, 1.25, ['Excellent','Very Good','Good'], ['Excellent','Very Good','Good','Fair'], 'Good')
    set_grade(df, df_p, 62, 75, 1.10, ['Excellent','Very Good', 'Good','Fair'], ['Excellent','Very Good','Good','Fair'], 'Very Good')
    set_grade(df, df_p, 64, 72, 1.05, ['Excellent','Very Good', 'Good'], ['Excellent','Very Good','Good'], 'Excellent')

    return (df, df_rap_price_list)

def run(file_date):
    df, df_rap_price_list = load_data(file_date)

    write_excel(df, wp_path, file_date, df_rap_price_list)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--date', help='date to process')
    args = parser.parse_args()
    file_date = datetime.now().strftime("%Y%m%d")
    if args.date:
        file_date = args.date
    run(file_date)
