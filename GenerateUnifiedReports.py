from os import listdir
from os.path import isfile, join
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

group_force = parser.add_argument_group('forcegroup')

group_force.add_argument( '-f', action='store_true', dest='force_generate',help='Force the generation of all unified reports.',default=False)

group_yearmonth_range = parser.add_argument_group('yearmonth_range_group')

group_yearmonth_range.add_argument( '-sy', action='store', dest='start_year',help='Sets the start year of reports to generate.',type=int)
group_yearmonth_range.add_argument( '-sm', action='store', dest='start_month',help='Sets the start month of reports to generate.',type=int)
group_yearmonth_range.add_argument( '-ey', action='store', dest='end_year',help='Sets the end year of reports to generate.',type=int)
group_yearmonth_range.add_argument( '-em', action='store', dest='end_month',help='Sets the end month of reports to generate.',type=int)

group_yearmonth = parser.add_argument_group('yearmonth_group')

group_yearmonth.add_argument( '-y', action='store', dest='year',help='Sets the year of reports to generate.',type=int)
group_yearmonth.add_argument( '-m', action='store', dest='month',help='Sets the month of reports to generate.',type=int)

#parser.add_argument( '-end', metavar='end year / month', nargs='2')

#GenerateUnifiedRecord( paypal_filename, unified_filename )

results = parser.parse_args()

class YearMonth():
    def __init__( self, year, month ):
        self.year = year
        self.month = month
    
    def greaterThan( self, ym ):
        if self.year > ym.year:
            return True
        elif self.year < ym.year:
            return False
        elif self.month > ym.month:
            return True
        return False
        
    def lessThan( self, ym ):
        if self.year < ym.year:
            return True
        elif self.year > ym.year:
            return False
        elif self.month < ym.month:
            return True
        return False
        
    def equal( self, ym ):
        if self.year == ym.year and self.month == ym.month:
            return True
        return False
        
    @staticmethod
    def min( a, b ):
        if a.lessThan( b ):
            return a
        return b
       
    @staticmethod
    def max( a, b ):
        if a.greaterThan( b ):
            return a
        return b
        
    def isValid( self ):
        if month in range( 1, 13 ) and year > 0:
            return True
        return False
            
        
    def plusOne( self ):
        if self.month is 12:
            return YearMonth( self.year + 1, 1 )
        return YearMonth( self.year, self.month + 1 )

class YearMonthRange():
    def __init__( self, startYM, endYM ):
        self.startYM = startYM
        self.endYM = endYM    
        
    def isValid( self ):
        if self.startYM.lessThan( self.endYM ) or self.startYM.equal( self.endYM ):
            return True
        return False

        
def ValidateYearMonthList( list ):
    for i in range( len( list ) - 1 ):
        if not list[ i ].plusOne().equal( list[ i + 1 ] ):
            return False
    return True     
        
def GenerateYearMonthList( path ):
    files = [ file for file in listdir( path ) if isfile(join(path,file)) ] 
    yearMonthList = []
    for filename in files:
        filenameTokens = filename.split("_")
        year = int( filenameTokens[1] )
        month = int( filenameTokens[2].split('.')[0] )
        yearMonthList.append( YearMonth( year, month ) )
        
    return yearMonthList    
        
   
def GetFullYRM():
    sy = 0
    sm = 0
    ey = 0
    em = 0    
    return YearMonthRange( YearMonth( sy, sm ), YearMonth( ey, em ) )
    
def GetMissingYMR():
    sy = 0
    sm = 0
    ey = 0
    em = 0    
    return YearMonthRange( YearMonth( sy, sm ), YearMonth( ey, em ) )
    

def YearMonthInList( ym, list ):
    for i in list:
        if ym.equal( i ):
            return True
    return False
    
    
def MissingUnifiedRange( paypalYMList, unifiedYMList ):
    missingList = []
    for ym in paypalYMList:
        if not YearMonthInList( ym, unifiedYMList ):
            missingList.append( ym )
    return missingList




    
    
if results.force_generate:
    ymr = GetFullYRM()
elif results.year and results.month:
    ymr = YearMonthRange( YearMonth( results.year, results.month ), YearMonth( results.year, results.month ) )
elif results.start_year and results.start_month and results.end_year and results.end_month:
    ymr = YearMonthRange( YearMonth( results.start_year, results.start_month ), YearMonth( results.end_year, results.end_month ) )
else:
    ymr = GetMissingYMR()

if not ymr.isValid():
    print "Error: not a valid range of year/months."

payPalYMList = GenerateYearMonthList( "paypal_records" )
print ValidateYearMonthList( payPalYMList )
# TODO: generate website records per type (donations, fundraisers, tickets, refunds)
#websiteDonationsYMList = GenerateYearMonthList( "website_donations" )
#websiteFundraisersYMList = GenerateYearMonthList( "website_fundraisers" )
#websiteTicketsYMList = GenerateYearMonthList( "website_tickets" )
#websiteRefundsYMList = GenerateYearMonthList( "website_refunds" )

# TODO: generate unified records
unifiedYMList = GenerateYearMonthList( "unified_records" )
print ValidateYearMonthList( unifiedYMList )

missingList = MissingUnifiedRange( payPalYMList, unifiedYMList )
for ym in missingList:
    print str( ym.year ) + "_" + str( ym.month )
    


