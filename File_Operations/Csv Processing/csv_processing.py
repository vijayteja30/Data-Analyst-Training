import csv
import os


# Doc: https://realpython.com/python-csv/

# file_path = os.path.join(os.getcwd(), 'File_Operations/Csv Processing/employee_birthday.csv')

# with open(file_path, 'r') as fp:
#     reader = csv.DictReader(fp, delimiter=',')
#     for row in reader:
#         print(row)




# import csv

# file_path = os.path.join(os.getcwd(), 'File_Operations/Csv Processing/employee_file.csv')
# with open(file_path, mode='w') as employee_file:
#     employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

#     employee_writer.writerow(['John Smith', 'Accounting', 'November'])
#     employee_writer.writerow(['Erica Meyers', 'IT', 'March'])



import csv
file_path = os.path.join(os.getcwd(), 'File_Operations/Csv Processing/employee_file2.csv')
with open(file_path, mode='w') as csv_file:
    fieldnames = ['emp_name', 'dept', 'birth_month']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'emp_name': 'John Smith', 'dept': 'Accounting', 'birth_month': 'November'})
    writer.writerow({'emp_name': 'Erica Meyers', 'dept': 'IT', 'birth_month': 'March'})