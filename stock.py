import json

def crawler(start_date, end_date):

    from yahoo_finance import Share

    pre_codes = open('codes', 'r')
    codes = json.load(pre_codes)
    pre_codes.close()

    data = []
    for code in codes:
        data.append(Share(code).get_historical(start_date, end_date))

    saved_data = open('saved_data', 'w')
    json.dump(data, saved_data)
    saved_data.close()

def analyzer(NUM, CHA, SLO, COR):

    temp_data = open('saved_data', 'r')
    saved_data = json.load(temp_data)
    temp_data.close()

    change = []
    daily_change = 0
    for company in saved_data:
        for daily in company:
            daily_change += (float(daily['High']) - float(daily['Low']))
        change.append((company[0]['Symbol'][:4], round(daily_change, 2)))

    pre_regression = []
    for company in saved_data:
        coordinates = []
        coordinates.append(company[0]['Symbol'][:4])
        for daily in company:
            date = daily['Date']
            x_coordinate = (int(date[0:4]) - 2016) * 365
            month = int(date[5:7])
            if   month == 1:
                pass
            elif month == 2:
                x_coordinate += 31
            elif month == 3:
                x_coordinate += 59
            elif month == 4:
                x_coordinate += 90
            elif month == 5:
                x_coordinate += 120
            elif month == 6:
                x_coordinate += 151
            elif month == 7:
                x_coordinate += 181
            elif month == 8:
                x_coordinate += 212
            elif month == 9:
                x_coordinate += 243
            elif month == 10:
                x_coordinate += 273
            elif month == 11:
                x_coordinate += 304
            else:
                x_coordinate += 334
            x_coordinate += int(date[8:10])
            coordinates.append((x_coordinate, float(daily['Close'])))
        pre_regression.append(coordinates)

    pre_lines = pre_regression

    regression = []
    for company in pre_regression:
        x_total, y_total = 0, 0
        for i in range(1, len(company)):
            x_total += company[i][0]
            y_total += company[i][1]
        ux = float(x_total) / (len(company) - 1)
        uy = float(y_total) / (len(company) - 1)
        regression.append([company[0], (round(ux, 2), round(uy, 2))])
        for coordinate in company[1:]:
            regression[len(regression) - 1].append(coordinate)

    slope = []
    correlation = []
    for company in regression:
        Sxx, Syy, Sxy = 0, 0, 0
        ux, uy = company[1][0], company[1][1]
        for i in range(2, len(company)):
            Sxx += (company[i][0] - ux) ** 2
            Syy += (company[i][1] - uy) ** 2
            Sxy += (company[i][0] - ux) * (company[i][1] - uy)
        a = float(Sxy) / Sxx
        r = float(Sxy) / ((Sxx ** 0.5) * (Syy ** 0.5))
        slope.append((company[0], round(a, 4)))
        correlation.append((company[0], round(r ** 2, 4)))

    sorted_change = []
    while len(change) > 0:
        pi = 0
        picked = change[pi][1]
        for i in range(len(change)):
            if change[i][1] < picked:
                picked = change[i][1]
                pi = i
        sorted_change.append(change[pi])
        change.remove(change[pi])

    sorted_correlation = []
    while len(correlation) > 0:
        pi = 0
        picked = correlation[pi][1]
        for i in range(len(correlation)):
            if correlation[i][1] > picked:
                picked = correlation[i][1]
                pi = i
        sorted_correlation.append(correlation[pi])
        correlation.remove(correlation[pi])

    sorted_slope = []
    while len(slope) > 0:
        pi = 0
        picked = slope[pi][1]
        for i in range(len(slope)):
            if slope[i][1] > picked:
                picked = slope[i][1]
                pi = i
        sorted_slope.append(slope[pi])
        slope.remove(slope[pi])

    score = []

    if CHA == True:
        for i in range(len(sorted_change)):
            score.append([sorted_change[i][0], i])

    if SLO == True:
        if CHA == True:
            for i in range(len(sorted_slope)):
                for company in score:
                    if company[0] == sorted_slope[i][0]:
                        company[1] += i
                        break
        else:
            for i in range(len(sorted_slope)):
                score.append([sorted_slope[i][0], i])

    if COR == True:
        if CHA == True or SLO == True:
            for i in range(len(sorted_correlation)):
                for company in score:
                    if company[0] == sorted_correlation[i][0]:
                        company[1] += i
                        break
        else:
            for i in range(len(sorted_correlation)):
                score.append([sorted_correlation[i][0], i])

    sorted_score = []
    while len(score) > 0:
        pi = 0
        picked = score[pi][1]
        for i in range(len(score)):
            if score[i][1] < picked:
                picked = score[i][1]
                pi = i
        sorted_score.append(score[pi])
        score.remove(score[pi])

    if NUM != False:
        sorted_score = sorted_score[NUM[0] - 1 : NUM[1]]

    for company in sorted_score:
        print(company[0], end = ' ')

    return sorted_score, pre_lines

def plotter(NUM, CHA, SLO, COR):

    import plotly.plotly as pp
    import plotly.graph_objs as pgo

    sorted_score, pre_lines = analyzer(NUM, CHA, SLO, COR)

    lines = []
    for company in sorted_score:
        x, y = [], []
        for line_company in pre_lines:
            if line_company[0] == company[0]:
                for ci in range(1, len(line_company)):
                    x.append(line_company[ci][0])
                    y.append(line_company[ci][1])
                lines.append(pgo.Scatter(x = x, y = y, mode = 'lines', name = company[0]))
                pre_lines.remove(line_company)
                break

    pp.iplot(lines, filename = 'NUM' + str(NUM) + 'CHA' + str(CHA) + 'SLO' + str(SLO) + 'COR' + str(COR))

analyzer(NUM = (1, 25), CHA = 0, SLO = 1, COR = 1)