def validate_spreadsheet():
    print('spreadsheet!')
    
def validate_userdata():
    print('data')

def main():
    while True:
        option = input('\nEnter your desired option (1 /2): ')
        if option.strip() == '1':
            validate_spreadsheet()
            break
        elif option.strip() == '2':
            validate_userdata()
            break
        else:
            continue

if __name__ == '__main__':
    main()