import datetime
import os,shutil

typestr = '%Y/%m/%d'

def str_to_datetime(string):
    return datetime.datetime.strptime(string, typestr)

def datetime_to_string(dt):
    return dt.strftime(typestr)

def get_grail(infile):
    grails = []
    with open(infile, 'r') as f:
        for line in f:
            if len(line) <= 1:
                continue
            items = line.replace('\t', ' ').replace('  ', ' ').split(' ')[:-1]
            line_date = items[0].split(',')[0]

            grail = {
                'chg': 0
            }

            try:
                grail['chg'] = float(items[6]) / 100
            except:
                pass

            grails.append({
                'date': str_to_datetime(line_date.replace('-', '/')),
                'info': grail
            })
            
        return grails

def get_sing(infile):
    sings = []
    with open(infile, 'r') as f:
        for line in f:
            if len(line) <= 1:
                continue
            if not (line[0] == '1' or line[0] == '2'):
                continue
            items = line.replace('\t', ' ').replace('  ', ' ').split(' ')[:-1]
            line_date = items[0].split(',')[0]

            sing = {
                'chg': 0,               # 涨幅
                'volume': 0,            # 总手
                'rate': 0,              # 超额收益率
                'vol_chg': 0,           # 成交量涨幅
                'relation': (False, False),
                'RSI': 0,               # RSI
                'price': {
                    'opening': 0,       # 开盘
                    'closing': 0,       # 收盘
                    'highest': 0,       # 最高
                    'lowest': 0,        # 最低
                    'avg': 0            # 平均
                },
                'KDJ': {
                    'RSV': 50,          # RSV
                    'K': 50,            # K
                    'D': 50,            # D
                    'J': 50             # J
                }
            }
            try:
                sing['volume'] = int(items[5])
            except:
                pass
            
            sing['price']['opening'] = float(items[1])
            sing['price']['highest'] = float(items[2])            
            sing['price']['lowest'] = float(items[3])
            sing['price']['closing'] = float(items[4])
            sing['price']['avg'] = (float(items[1]) + float(items[2]) + float(items[3]) + float(items[4])) / 4

            sings.append({
                'date': str_to_datetime(line_date),
                'info': sing
            })

    return sings

def change(sings):
    first = True
    former = 0
    for sing in sings:
        if first:
            sing['info']['chg'] = 0
            first = False
        else:
            sing['info']['chg'] = (sing['info']['price']['closing'] - former) / former
        
        former = sing['info']['price']['closing']

def pure_regression(grails, sings, year):
    formerx = []
    formery = []
    for grail, sing in zip(grails, sings):
        try:
            if grail['date'].year < year:
                formerx.append(grail['info']['chg'])
                formery.append(sing['info']['chg'])
        except Exception as e:
            continue

    x = formerx[1:]
    y = formery[1:]
    arrlen = len(x)
    if arrlen != len(y):
        print("arr not equal")
        exit(1)

    s_xy = 0
    s_x = 0
    s_y = 0
    s_square_x = 0

    for (xi, yi) in zip(x, y):
        s_xy += xi * yi
        s_x += xi
        s_y += yi
        s_square_x += xi * xi
        
    gradient = (arrlen * s_xy - s_x * s_y) / (arrlen * s_square_x - s_x * s_x)
    intercept = s_y / arrlen - s_x * gradient / arrlen

    square_delta = 0
    for (xi, yi) in zip(x, y):
        square_delta +=  (yi - s_y / arrlen) ** 2

    square_delta /= (arrlen - 2)
    return gradient, intercept, s_square_x

# 2
def diff_rate(grails, sings, gradient, year):
    for grail, sing in zip(grails, sings):
        if grail['date'].year < year:
            continue
        sing['info']['rate'] = sing['info']['chg'] - grail['info']['chg'] * gradient

# 3
def volume(sings):
    first = True
    former = 0
    for sing in sings:
        if first:
            sing['info']['vol_chg'] = 0
            first = False
        else:
            sing['info']['vol_chg'] = (sing['info']['volume'] - former) / former

        former = sing['info']['volume']

# 4, 5
def relationship(sings):
    for sing in sings:
        sing['info']['relation'] = (False, False) if sing['info']['vol_chg'] <= 0 else (sing['info']['chg'] > 0, sing['info']['chg'] < 0)

# rsi
# 一个日期及其前 time_range 天的RSI值
def RSI(sings, time_range):
    day_lis = []
    for sing in sings:
        day_lis.append(sing['info']['chg'])
        if len(day_lis) > time_range:
            day_lis.pop(0)

        inc = 0
        dec = 0
        for elem in day_lis:
            if elem > 0:
                inc += elem
            else:
                dec -= elem

        sing['info']['RSI'] = 100 * inc / (inc + dec)

def end_RSI(sings, time_range):
    day_lis = []
    last = 0
    for sing in sings:
        day_lis.append(sing['info']['price']['closing'] - last)
        last = sing['info']['price']['closing']
        if len(day_lis) > time_range:
            day_lis.pop(0)

        inc = 0
        dec = 0
        for elem in day_lis:
            if elem > 0:
                inc += elem
            else:
                dec -= elem

        sing['info']['RSI'] = 100 * inc / (inc + dec)

def KDJ(sings, time_range):
    day_lis = []
    last = {
        'K': 50,
        'D': 50
    }
    for sing in sings:
        day_lis.append(sing['info']['price']['closing'])
        if len(day_lis) > time_range:
            day_lis.pop(0)

        # RSV
        sing['info']['KDJ']['RSV'] = 50 if len(day_lis) == 1 else 100 * (sing['info']['price']['closing'] - min(day_lis)) / (max(day_lis) - min(day_lis))

        # K
        sing['info']['KDJ']['K'] = (2 / 3) * last['K'] + (1 / 3) * sing['info']['KDJ']['RSV']

        # D
        sing['info']['KDJ']['D'] = (2 / 3) * last['D'] + (1 / 3) * sing['info']['KDJ']['K']

        # J
        sing['info']['KDJ']['J'] = 3 * sing['info']['KDJ']['K'] - 2 * sing['info']['KDJ']['D']

        last['K'] = sing['info']['KDJ']['K']
        last['D'] = sing['info']['KDJ']['D']

def filter(lis, year):
    new_lis = []
    for day in lis:
        if day['date'].year >= year:
            new_lis.append(day)
    return new_lis

def match(grails, sings):
    new_grail = []
    its = iter(sings)
    itd = iter(grails)

    x = next(itd)
    y = next(its)
    while True:
        try:
            while x['date'] < y['date']:
                x = next(itd)
            if x['date'] == y['date']:
                new_grail.append(x)
            
            y = next(its)
        except StopIteration:
            break

    return new_grail

def write_list(lis, outfile):
    out = open(outfile, 'w')
    for elem in lis:
        out.write('%s %s\n' % (datetime_to_string(elem['date']), str(elem['info'])))

def calc_sing(year, time_range, grail, stock_in, out_path, gradient_path, log_path):
    
    l = open(log_path, 'a+')

    stock = get_sing(stock_in)
    change(stock)

    new_grail = match(grail, stock)
    try:
        reg_rate, diff, ss = pure_regression(new_grail, stock, year)
    except:
        print('bad ' + os.path.split(stock_in)[1][:-4])
        l.write('bad ' + os.path.split(stock_in)[1][:-4] + '\n')
        return
    new_stock = filter(stock, year)
    new_grail = filter(new_grail, year)

    del stock

    diff_rate(new_grail, new_stock, reg_rate, year)
    volume(new_stock)
    relationship(new_stock)

    RSI(new_stock, time_range)
    KDJ(new_stock, time_range)

    # output
    write_list(new_stock, os.path.join(out_path, os.path.split(stock_in)[1]))

    with open(gradient_path, 'a+') as f:
        f.write('%s,%f,%f,%f\n' % (os.path.split(stock_in)[1][:-4], reg_rate, diff, ss))
    
    l.write(os.path.split(stock_in)[1][:-4] + '\n')
    print(os.path.split(stock_in)[1][:-4])

    del new_grail

def main_func():
    cwd = os.getcwd()
    root_in = os.path.join(cwd, 'input')
    root_out = os.path.join(cwd, 'output')
    grail = get_grail(os.path.join(cwd, 'grail.txt'))
    gradient_path = os.path.join(cwd, 'gradient.txt')
    log_path = os.path.join(cwd, 'log.txt')

    if os.path.exists(gradient_path):
        os.remove(gradient_path)
    if os.path.exists(log_path):
        os.remove(log_path)

    if not os.path.exists(root_out):
        os.makedirs(root_out)

    for (rootname, dirs, files) in os.walk(root_in):
        # f is a string(not a file object)
        for f in files:
            whole_path = os.path.join(rootname, f)
            calc_sing(2016, 10, grail, whole_path, root_out, gradient_path, log_path)

main_func()