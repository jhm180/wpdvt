



clarity_allow = {"IF":1, "VVS1":2, "VVS2":3, "VS1":4, "VS2":5, "SI1":5, "SI2":7, "I1":8, "I2":9}
color_allow = {"D":1, "E":2, "F":3, "G":4, "H":5, "I":6, "J":7, "K":8, "L":9, "M":10, "N":11}


def check_values(value, key, err):
	if key == "clarity":
		ok_vals = clarity_allow
	elif key == "color":
		ok_vals = color_allow
	else:
		ok_vals = "ERR"
	if value in ok_vals.keys():
		pass
	else:
		err.append("Invalid value for {0} - Allowable values are {1}. \n".format(key, ok_vals.keys()))


def get_curve_key(weight):
    if weight >= 0.01 and weight <= 0.03:
        return 'r01'
    elif weight >= 0.04 and weight <= 0.07:
        return 'r04'
    elif weight >= 0.08 and weight <= 0.14:
        return 'r08'
    elif weight >= 0.15 and weight <= 0.17:
        return 'r15'
    elif weight >= 0.18 and weight <= 0.22:
        return 'r18'
    elif weight >= 0.23 and weight <= 0.29:
        return 'r23'
    elif weight >= 0.30 and weight <= 0.39:
        return 'r30'
    elif weight >= 0.40 and weight <= 0.49:
        return 'r40'
    elif weight >= 0.50 and weight <= 0.59:
        return 'r50'
    elif 0.60 <= weight and weight <= 0.69:
        return 'r60'
    elif 0.70 <= weight and weight <= 0.79:
        return 'r70'
    elif 0.80 <= weight and weight <= 0.89:
        return 'r80'
    elif 0.90 <= weight and weight <= 0.99:
        return 'r90'
    elif 1.00 <= weight and weight <= 1.49:
        return 'rc1'
    elif 1.50 <= weight and weight <= 1.99:
        return 'rcr'
    elif 2.00 <= weight and weight <= 2.99:
        return 'rc2'
    elif 3.00 <= weight and weight <= 3.99:
        return 'rc3'
    elif 4.00 <= weight and weight <= 4.99:
        return 'rc4'
    elif 5.00 <= weight and weight <= 9.99:
        return 'rc5'
    else:
        return 'rct'

def get_price_params(json):
    clar = json['clarity']
    color = json['color']
    shape_key = ""
    weight_key = get_curve_key(json['weight'])
    if json['shape'].lower() == "round":
        shape_key = "RB"
    else:
        shape_key = "PR"
    return "{0}_{1}_{2}_{3}".format(shape_key, color, clar, weight_key)




