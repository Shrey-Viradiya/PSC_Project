import csv
with open('ratings.csv', newline='\n', encoding='utf-8') as csvfile, open('ratings2.csv','w',newline='\n') as userfile:
    rdr = csv.reader(csvfile, delimiter=',')
    wrt = csv.writer(userfile, delimiter=',')
    for row in rdr:
        try:
            x = float(row[3])
            wrt.writerow([row[x] for x in range(1,4)])
        except:
            pass

# import pandas as pd
#
# df = pd.read_csv('BX-Book-Ratings.csv', delimiter=';')
# print(df)
#
# df.to_csv('ratings.csv', sep=',')

# import pandas as pd
#
# df = pd.read_csv('books.csv')
#
# df.columns = ['ISBN', 'Title', 'Author', 'Year', 'Publisher']
#
# df['Year'] = pd.to_numeric(df['Year'])