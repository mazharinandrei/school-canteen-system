import pandas as pd


def main():
    #with open('Цикличное меню.csv') as f:
    file = pd.read_csv('Цикличное меню.csv')
    file.head()

if __name__ == '__main__':
    main()