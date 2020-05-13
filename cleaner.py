import sys

#Function to parse keywords file
def get_keywords(path_to_file):

    #Get list of keywords from separate txt file and parse them into a python dictionary
    keyword_file = open(path_to_file,'r')
    keyword_lst = keyword_file.readlines()
    keyword_dict = {}
    current_section = ''
    for i in range(len(keyword_lst)):
        if '#' in keyword_lst[i]:
            current_section = keyword_lst[i][1:-1]
            keyword_dict[current_section] = []
        else:
            keyword_dict[current_section].append(keyword_lst[i][:-1].split(': '))
    return keyword_dict



#Function to parse csv file to a python list
def parse_csv(path_to_file):
    csv_lst_new = [{}] #initialise list with one dictionary inside
    header_lst = [] #initialise empty list for headers

    csv_file = open(path_to_file,'r')
    csv_lst = csv_file.readlines()

    for i in csv_lst:
        separated_values = i.split(',') #split each csv line into a list
        #detect and parse overall account data into the first dictionary
        if len(separated_values) == 2:
            csv_lst_new[0][separated_values[0]] = separated_values[1][:-1]

        #parse first row of real csv data as headers and puts it into header_lst variable
        elif len(separated_values) > 2 and len(header_lst) == 0:
            for i in separated_values:
                if '\n' in i:
                    header_lst.append(i[:-1])
                else:
                    header_lst.append(i)

        #parse subsequent rows of csv data and appends it as a dictionary using known headers
        elif len(separated_values) > 2 and len(header_lst) > 0:
            temp_dict = {}
            for i in range(len(header_lst)):
                temp_dict[header_lst[i]] = separated_values[i]
            csv_lst_new.append(temp_dict)

    return csv_lst_new

#Main function
def main():

    keywords_path = 'keywords.txt'

    if len(sys.argv) > 4: #Checks for too many arguments
        print("Too many arguments!")
        return None
    elif len(sys.argv) < 2: #Checks for too few arguments
        print("Too few arguments!")
        return None
    elif len(sys.argv) == 3: #Update paths accordingly
        csv_path = sys.argv[1]
        keywords_path = sys.argv[2]
    elif len(sys.argv) == 2:
        csv_path = sys.argv[1]

    #Call get_keywords() function to parse keywords file
    keyword_dictionary = get_keywords(keywords_path)
    #print(keyword_dictionary)

    #Call parse_csv() function to parse csv file
    csv_lst = parse_csv(csv_path)

    new_csv_lst = [['Expense','Location','Debit Amount','Credit Amount','Date','Category','Transaction Type','Comment']] # initialise new list for output data
    header_output = {'Expense':0,'Location':1,'Debit Amount':2,'Credit Amount':3,'Date':4,'Category':5,'Transaction Type':6,'Comment':7}

    #input data order : Transaction Date,Reference,Debit Amount,Credit Amount,Transaction Ref1,Transaction Ref2,Transaction Ref3
    #output data order: Expense,Location,Debit Amount,Credit Amount,Date,Category,Transaction Type,Comment
    for i in range(1,len(csv_lst),1):

        #Initialise empty template
        temp_lst = ['','','','','','','','']

        #Copy over Debit and Credit Amounts
        temp_lst[header_output['Debit Amount']] = csv_lst[i]['Debit Amount'][1:]
        temp_lst[header_output['Credit Amount']] = csv_lst[i]['Credit Amount'][1:]

        #Parse dates of transactions and References
        if csv_lst[i]['Reference'] == 'UMC-' or csv_lst[i]['Reference'] == 'UMC-S': # For UMC Transactions

            #UMC transactions have their real transaction dates written in the references
            temp_lst[header_output['Date']] = csv_lst[i]['Transaction Ref1'][-5:-3]+' '+csv_lst[i]['Transaction Ref1'][-3:-2]+csv_lst[i]['Transaction Ref1'][-2:].lower()

            #Detect new year rollover of months when parsing dates
            if temp_lst[header_output['Date']][-3:] == 'Dec' and csv_lst[i]['Transaction Date'][3:6] == 'Jan':
                temp_lst[header_output['Date']] += ' '+str(int(csv_lst[i]['Transaction Date'][-4:])-1)
            else:
                temp_lst[header_output['Date']] += ' '+csv_lst[i]['Transaction Date'][-4:]

            #Parse Transaction References
            temp_lst[header_output['Expense']] = csv_lst[i]['Transaction Ref1'][:-11].split('-')[0]
            if len(csv_lst[i]['Transaction Ref1'].split('-')) == 2:
                temp_lst[header_output['Location']] = csv_lst[i]['Transaction Ref1'][:-11].split('-')[1]
            elif len(csv_lst[i]['Transaction Ref1'].split('-')) > 2:
                for j in range(1,len(csv_lst[i]['Transaction Ref1'][:-11].split('-'))-1,1):
                    temp_lst[header_output['Expense']] += '-' + csv_lst[i]['Transaction Ref1'][:-11].split('-')[j]
                temp_lst[header_output['Location']] = csv_lst[i]['Transaction Ref1'][:-11].split('-')[-1]

            #Remove Whitespace
            temp_lst[header_output['Expense']] = temp_lst[header_output['Expense']].strip()
            temp_lst[header_output['Location']] = temp_lst[header_output['Location']].strip()

            #Parse in Transaction Type
            temp_lst[header_output['Transaction Type']] = 'Debit/Credit Card'

        else: #For non UMC transactions

            # Non UMC transactions are logged immediately so the dates simply carry over
            temp_lst[header_output['Date']] = csv_lst[i]['Transaction Date']

            #Parse Transaction References for NETS and NETS QR Payment
            if csv_lst[i]['Reference'] == 'POS':
                if 'NETS QR PAYMENT' in csv_lst[i]['Transaction Ref1']: #For NETS QR Payment/Refund
                    temp_lst[header_output['Transaction Type']] = 'NETS QR Payment'
                    temp_lst[header_output['Expense']] = csv_lst[i]['Transaction Ref2'][4:]
                elif 'NETS QR REFUND' in csv_lst[i]['Transaction Ref1']:
                    temp_lst[header_output['Transaction Type']] = 'NETS QR Refund'
                    temp_lst[header_output['Expense']] = 'Refund'
                elif 'NETS' in csv_lst[i]['Transaction Ref3']: # For NETS
                    temp_lst[header_output['Transaction Type']] = 'NETS'
                    temp_lst[header_output['Expense']] = csv_lst[i]['Transaction Ref2']

            #Parse Transaction Reference for Bank Transfers
            if csv_lst[i]['Reference'] == 'ICT':
                temp_lst[header_output['Transaction Type']] = 'Bank Transfer'
                if 'PayNow' in csv_lst[i]['Transaction Ref1']:
                    temp_lst[header_output['Expense']] = 'PayNow ' + csv_lst[i]['Transaction Ref2']
                    if 'OTHR' in csv_lst[i]['Transaction Ref3']:
                        temp_lst[header_output['Comment']] = csv_lst[i]['Transaction Ref3'][5:]
                else:
                    temp_lst[header_output['Expense']] = csv_lst[i]['Transaction Ref1'] + ' ' + csv_lst[i]['Transaction Ref2']

            #Parse Transaction Reference for PayLah
            if csv_lst[i]['Reference'] == 'ITR':
                if 'MAXED OUT FROM PAYLAH! :' in csv_lst[i]['Transaction Ref1']:
                    temp_lst[header_output['Expense']] = 'PayLah from ' + csv_lst[i]['Transaction Ref2']
                    temp_lst[header_output['Transaction Type']] = 'PayLah!'
                if 'TOP-UP TO PAYLAH! :' in csv_lst[i]['Transaction Ref1']:
                    temp_lst[header_output['Expense']] = 'PayLah Topup'
                    temp_lst[header_output['Transaction Type']] = 'PayLah!'

            #Parse Transaction Reference for CAM
            if csv_lst[i]['Reference'] == 'CAM':
                temp_lst[header_output['Expense']] = csv_lst[i]['Transaction Ref2']

            #Parse Transaction Reference for IBG
            if csv_lst[i]['Reference'] == 'IBG':
                temp_lst[header_output['Expense']] = csv_lst[i]['Transaction Ref1'] + ' ' + csv_lst[i]['Transaction Ref2']

            #Parse Transaction Reference for INT
            if csv_lst[i]['Reference'] == 'INT':
                temp_lst[header_output['Expense']] = 'Bank Interest'

        if csv_lst[i]['Reference'] != 'AWL':
            new_csv_lst.append(temp_lst)

    for i in new_csv_lst:
        print(i)
        for j in keyword_dictionary['Location']:
            if j[0] in i[header_output['Expense']] and i[header_output['Location']] == '':
                i[header_output['Location']] = j[1]
            if i[header_output['Location']].isupper() and j[0] in i[header_output['Location']]:
                i[header_output['Location']] = j[1]
        for j in keyword_dictionary['Transaction Type']:
            if j[0] in i[header_output['Expense']]:
                i[header_output['Transaction Type']] = j[1]
        for j in keyword_dictionary['Expense']:
            if j[0] in i[header_output['Expense']]:
                i[header_output['Expense']] = j[1]
                i[header_output['Category']] = j[2]
        temp_str = i[header_output['Expense']] + '-' + i[header_output['Location']]
        for j in keyword_dictionary['Weird Exceptions']:
            if j[0] in temp_str:
                i[header_output['Expense']] = j[1]
                i[header_output['Location']] = ''
                i[header_output['Category']] = j[2]

    #Set the path of the new outputfile
    #Output file will be in the same location and name
    #With a _new appended to the name
    new_file_path = csv_path.split('.csv')[0]
    new_file_path += '_new.csv'

    #Write to new file
    new_file = open(new_file_path,'w')
    for i in new_csv_lst:
        for j in range(len(i)-1):
            new_file.write(i[j] + ',')
        new_file.write(i[-1] +'\n')
    new_file.close()
    return None

if __name__ == "__main__":
    main()
