import argparse



# Read options on which PayPal records to process (year / month) or run on discovery to find the files or discover new files and generate new unified files but preserve the old ones (default)
# load all the Website records based on discovery
# load the PayPal monthly report(s)
# reconsile each record in PayPal records to identify the event and standardize the fields
# save to file the unified records


# GenerateUnifiedReports.py [no options] - this will discover which PayPay files exist wihtout corrisponsiding unified record files and generate the missing unified record files.
# GenerateUnifiedReports.py -f - this will force the generation of all unfied record files even if they already exist
# GenerateUnifiedReports.py -start 2012 01 -end 2013 07 - this will generate the unified record files for the range specified. (start year, start month, end year, end month)


parser = argparse.ArgumentParser( description='Process options for generating unified reports')
parser.add_argument( '-force', metavar='force generate')
parser.add_argument( '-start', metavar='start year / month', nargs='2')
parser.add_argument( '-end', metavar='end year / month', nargs='2')

#GenerateUnifiedRecord( paypal_filename, unified_filename )
