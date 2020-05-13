# About
A python script to reformat CSVs in a certain format into another format.  
Also has the ability to replace strings based on keywords found in the `keywords.txt` file  
Currently focused on using this to reformat bank transaction CSVs and has lots of hard coded bits because my break week is only this long

Transaction Codes are referenced from https://www.dbs.com.sg/personal/support/bank-account-transaction-codes.html

# Future work
1. **Further modularisation of code**  
Currently the main() function contains most of the code and is rather long and chunky. I intend to separate it out into their own functions in order to make the code cleaner and easier to understand as well as debug and code

2. **Reduce the amount of hard coded bits**  
Hopefully in the future this can be a general use CSV reformatter and maybe even produce other types of ouput other than CSV
