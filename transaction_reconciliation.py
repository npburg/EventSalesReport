import re, csv, datetime, pytz



# Download the latest PayPal monthly records and website monthly records
# Run script to generate unified monthly records (input is the PayPal monthly records and all website records)
# Run script to generate monthly reports (input is the unified records)
# Run script to generate full report (input is monthly reports)

	
#######################################################################################################################
#
# Website filenames
#
#######################################################################################################################
refundsFilename 	= 'Refunds_20120101_20150228.csv' 	#'refunds_2012_10_16_to_2014_02_03.csv'
salesFilename 		= 'Tickets_20120101_20150228.csv'	#'paypal_transactions_2009_01_29_to_2014_02_05_mod.csv'
fundraiserFilename 	= 'Fundraisers_20120101_20150228.csv'	#'fundraisers_2013_05_30.csv'
donationsFilename	= 'Donations_20120101_20150228.csv'		#'donations_2012_12_15_to_2013_02_18.csv'
	
class WebsiteKeys():
    refunds = "Refunds"
    refunds_original = "Refunds Original"
    sales = "Sales"
    fundraisers = "Fundraisers"
    donations = "Donations"
    
    @staticmethod
    def list():
        return [ WebsiteKeys.refunds, WebsiteKeys.refunds_original, WebsiteKeys.sales, WebsiteKeys.fundraiser, WebsiteKeys.donations ]

    
    
paypalFolder = "paypal_records"
websiteFolder = "website_records"
	
#######################################################################################################################
#
# Generate transaction dictionary
#
# This function will load a csv file and generate a nested dictionary based on the records and keys provided.
# dict[ primaryKey ] = dict() so at each primaryKey there is a subdictionary with additional information based on 
# the stringKeys/floatKeys.  These keys are based on the header fields in the file and the stringKeys are fields
# that are of the string type while the floatKeys are of the float type.
#
# filename - name and path to file to open and read the cvs records
# transactionIDKey - primary key use to create dictionary
# stringKeys - list of string keys
# floatKeys - list of floating point number keys
#
# output - dictionary of the records from the file based on the keys provided
#
#######################################################################################################################
def GenerateTransactionDict( filename, transactionIDKey, stringKeys, floatKeys ):
	indexKeys = [ transactionIDKey ]
	indexKeys.extend( stringKeys )
	indexKeys.extend( floatKeys )
	
	indexDict = dict()	
	transactionDict = dict()

	header = True
	entry_index = 0
	
	with open( filename, 'r' ) as csvfile:
		reader = csv.reader( csvfile )
		for lineList in reader:
			if header:
				header = False
				# PayPal transaction has leading white space for some field headers
				lineList = [ field.strip() for field in lineList ]
				
				for key in indexKeys:
					indexDict[ key ] = lineList.index( key )
			else:			
				lineDict = dict()

				lineDict[ 'entry_index' ] = entry_index
				entry_index = entry_index + 1
				
				for key in stringKeys:
					field = lineList[ indexDict[ key ] ]
					lineDict[ key ] = field.translate( None, "'" ) 
					
				for key in floatKeys:
					field = lineList[ indexDict[ key ] ]
					try:
						lineDict[ key ] = float( field.translate( None, '",' ) )
					except:
						lineDict[ key ] = 0.0
					
				transactionIDString = lineList[ indexDict[ transactionIDKey ] ].translate( None, '"' )
				# workaround bad data in transaction field
				if not transactionIDString or transactionIDString.find( "Custom" ) != -1 or transactionIDString.find( "CHARGEBACK" ) != -1 or transactionIDString.find( "FREE" ) != -1:
					continue
					#print "GenerateTransactionDict: " + transactionIDString
				else:
					transactionDict[ transactionIDString ] = lineDict
	
	return transactionDict

	
#######################################################################################################################
#
# PrintTransactionRecord
#
#######################################################################################################################
def PrintTransactionRecord( recordDict, key ):
	print '\n\nTransaction ID: ' + key
	for subKey in recordDict:
		print subKey + ": " + str( recordDict[ subKey ] )

	
#######################################################################################################################
#
# PrintTransactionDict
#
#######################################################################################################################
def PrintTransactionDict( transactionDict ):
	for key, recordDict in transactionDict.iteritems():
		PrintTransactionRecord( recordDict, key )
		
	
#######################################################################################################################
#
# SaveTransactionDict
#
#######################################################################################################################
def SaveTransactionDict( filename, dict, fieldList ):

	with open( filename, 'wb' ) as csvfile:
		filewriter = csv.writer( csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL )
		
		filewriter.writerow( fieldList )
	
		for key in dict:
			row = [ key ]
			for field in fieldList[1:]:
				row.append( dict[ key ][ field ] )
			filewriter.writerow( row )
	
	
#######################################################################################################################
#
# DateTime_to_TimeStamp
#
#######################################################################################################################
def DateTime_to_TimeStamp( date, time, timezone ):
	
	date_list = date.split( '/' )
	time_list = time.split( ':' )

	if timezone.find( "PST" ) != -1:
		local_time_zone = pytz.timezone('US/Pacific')
	elif timezone.find( "PDT" ) != -1:
		local_time_zone = pytz.timezone('US/Mountain')
	else:
		print "error: unknown time zone"
		local_time_zone = pytz.utc
	
	now = datetime.datetime( int(date_list[ 2 ]), int(date_list[ 0 ]), int(date_list[ 1 ]), int(time_list[ 0 ]), int(time_list[ 1 ]), int(time_list[ 2 ]), tzinfo=local_time_zone )
	start = datetime.datetime( 1970, 1, 1, tzinfo=pytz.utc )
	
	return (now - start).total_seconds()

	
#######################################################################################################################
#
# GenerateUnifiedRecord
#
#######################################################################################################################
def GenerateUnifiedRecord( paypal_csv_filename, unified_csv_filename):

	paypal_transactionIDKey = 'Transaction ID'
	paypal_StringKeys 		= [ 'Reference Txn ID', 'Status', 'Date', 'Time', 'Time Zone', 'Type', 'Item Title', 'Item ID' ]
	paypal_floatKeys	 	= [ 'Gross', 'Fee', 'Net', 'Balance' ]
	payPalDict = GenerateTransactionDict( paypal_csv_filename, paypal_transactionIDKey, paypal_StringKeys, paypal_floatKeys )
	
	refund_transactionIDKey = 'refund_transaction_id'
	refund_StringKeys 		= [ 'event_id', 'name' ]
	refund_floatKeys	 	= [ ]
	refundsDict = GenerateTransactionDict( refundsFilename, refund_transactionIDKey, refund_StringKeys, refund_floatKeys )
	
	refund_original_transactionIDKey = 'original_transaction_id'
	refund_original_StringKeys 		= [ 'event_id', 'name' ]
	refund_original_floatKeys	 	= [ ]
	refunds_original_Dict = GenerateTransactionDict( refundsFilename, refund_original_transactionIDKey, refund_original_StringKeys, refund_original_floatKeys )
	
	sales_transactionIDKey 	= 'transaction_id'
	sales_StringKeys 		= [ 'event_id', 'name' ]
	sales_floatKeys	 		= [ ]
	salesDict = GenerateTransactionDict( salesFilename, sales_transactionIDKey, sales_StringKeys, sales_floatKeys )
	
	fundraiser_transactionIDKey = 'transaction_id'
	fundraiser_StringKeys 		= [ 'ticket_type' ]
	fundraiser_floatKeys	 	= [ ]
	fundraiserDict = GenerateTransactionDict( fundraiserFilename, fundraiser_transactionIDKey, fundraiser_StringKeys, fundraiser_floatKeys )
	
	donations_transactionIDKey 	= 'transaction_id'
	donations_StringKeys 		= [ 'event_id', 'name', 'identifier' ]
	donations_floatKeys	 		= [ ]
	donationsDict = GenerateTransactionDict( donationsFilename, donations_transactionIDKey, donations_StringKeys, donations_floatKeys )

	# TODO: generate error if paypal field keys match the field keys for the other records
	
	for key in payPalDict:
		#print key
		payPalDict[ key ][ 'event_id' ]   = '-1'
		payPalDict[ key ][ 'event_name' ] = 'NA'
		payPalDict[ key ][ 'lf_source' ]  = 'NA'
		payPalDict[ key ][ 'timestamp' ]  = DateTime_to_TimeStamp( payPalDict[ key ][ 'Date' ], payPalDict[ key ][ 'Time' ], payPalDict[ key ][ 'Time Zone' ])

	for key in payPalDict:
        # match the key to the refund record
		if key in refundsDict:
			payPalDict[ key ][ 'event_id' ] 	= refundsDict[ key ][ 'event_id' ]
			payPalDict[ key ][ 'event_name' ] 	= refundsDict[ key ][ 'name' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'refunds'
        # match the key to the refund record against the original id
		elif key in refunds_original_Dict:
			payPalDict[ key ][ 'event_id' ] 	= refunds_original_Dict[ key ][ 'event_id' ]
			payPalDict[ key ][ 'event_name' ] 	= refunds_original_Dict[ key ][ 'name' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'refunds'
        # match the key to the sale record
		elif key in salesDict:
			payPalDict[ key ][ 'event_id' ] 	= salesDict[ key ][ 'event_id' ]
			payPalDict[ key ][ 'event_name' ]	= salesDict[ key ][ 'name' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'sales'
        # match the key to the fundraiser record
        # set the event_id to -2 for fundraisers
		elif key in fundraiserDict:
			payPalDict[ key ][ 'event_id' ] 	= '-2'			
			payPalDict[ key ][ 'event_name' ]	= fundraiserDict[ key ][ 'ticket_type' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'fundraiser'
        # match the key to the dontations record
		elif key in donationsDict:
			payPalDict[ key ][ 'event_id' ] 	= donationsDict[ key ][ 'event_id' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'donations'
            # set the name to the field 'name' otherwise use the 'identifier'
			if donationsDict[ key ][ 'name' ].find( 'NULL' ) == -1:
				payPalDict[ key ][ 'event_name' ]	= donationsDict[ key ][ 'name' ]
			else:
				payPalDict[ key ][ 'event_name' ]	= donationsDict[ key ][ 'identifier' ]				
        # if key is not found in the primary key for the records need to check for other fields to match keys
        # check to see if PayPal Reference Txn ID is in sales record
        elif payPalDict[ key ][ 'Reference Txn ID' ] in salesDict:
			refKey = payPalDict[ key ][ 'Reference Txn ID' ]
			payPalDict[ key ][ 'event_id' ] 	= salesDict[ refKey ][ 'event_id' ]
			payPalDict[ key ][ 'event_name' ]	= salesDict[ refKey ][ 'name' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'Reference Txn ID'
        # if PayPal Item Title field exist for this key then set to this record
		elif payPalDict[ key ][ 'Item Title' ]:
			payPalDict[ key ][ 'event_id' ] = payPalDict[ key ][ 'Item ID' ]
			payPalDict[ key ][ 'event_name' ] = payPalDict[ key ][ 'Item Title' ]
			payPalDict[ key ][ 'lf_source' ] 	= 'PayPal Item Title'
        # Check record that was not matched to see if it was removed and mark as removed and print that its event was not found
		elif payPalDict[ key ][ 'Status' ].find( 'Removed' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-3'
			payPalDict[ key ][ 'event_name' ] 	= 'Removed'
			print "Removed:  " + "Unable to find event for: " + key + "  " + payPalDict[ key ][ 'Date' ]
		# Check record that was not matched to see if it was cancled and mark as canceled and print that its event was not found        
        elif payPalDict[ key ][ 'Status' ].find( 'Canceled' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-4'
			payPalDict[ key ][ 'event_name' ] 	= 'Canceled'
			print "Canceled:  " + "Unable to find event for: " + key + "  " + payPalDict[ key ][ 'Date' ]
		# Check for reocds of cancelled fees to log; however,
        # Cancelled fees are covered by attendee refund and do not affect the balance
		elif payPalDict[ key ][ 'Type' ].find( 'Cancelled Fee' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-5'
			payPalDict[ key ][ 'event_name' ] 	= 'Cancelled Fee'
        # Check for records of reversal and note that we were not able to find the event for this record.
		elif payPalDict[ key ][ 'Type' ].find( 'Reversal' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-6'
			payPalDict[ key ][ 'event_name' ] 	= 'Reversal'
			print "Reversal:  " + "Unable to find event for: " + key + "  " + payPalDict[ key ][ 'Date' ]
		# Transfers are not per event and are ok.
		elif payPalDict[ key ][ 'Type' ].find( 'Withdraw Funds to a Bank Account' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-7'
			payPalDict[ key ][ 'event_name' ] 	= 'Withdraw Funds to a Bank Account'
		# Check for recrods of refunds that are not associdated with an event and log that.
        elif payPalDict[ key ][ 'Type' ].find( 'Refund' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-8'
			payPalDict[ key ][ 'event_name' ] 	= 'Unknown - Refund'	
			print "Unknown - Refund:  " + "Unable to find event for: " + key + "  " + payPalDict[ key ][ 'Date' ]
		# PayPal card refund not per event and are ok.
		elif payPalDict[ key ][ 'Type' ].find( 'PayPal card confirmation refund' ) != -1:
			payPalDict[ key ][ 'event_id' ] 	= '-9'
			payPalDict[ key ][ 'event_name' ] 	= 'PayPal card confirmation refund'	
        # Catch all for records which are not covered by other conditions.
        # These records should be investigated to see why there is not a condition that matches this record.
		else:
			print "Unknown:  " + "Unable to find event for: " + key + "  " + payPalDict[ key ][ 'Date' ]

	SaveTransactionDict( unified_csv_filename, payPalDict, [ 'Transaction ID', 'entry_index', 'timestamp', 'Gross', 'Fee', 'Net', 'Balance', 'event_id', 'event_name', 'lf_source', 'Type', 'Status', 'Reference Txn ID', 'Item Title', 'Item ID' ] )
	

#######################################################################################################################
#
# GenerateMonthlyReport
#
#######################################################################################################################
def GenerateMonthlyReport( unified_filename, report_filename ):
	unified_transactionIDKey = 'Transaction ID'
	unified_StringKeys 		= [ 'event_id', 'event_name' ]
	unified_floatKeys	 	= [ 'Gross', 'Fee', 'Net' ]
	
	unifiedDict = GenerateTransactionDict( unified_filename, unified_transactionIDKey, unified_StringKeys, unified_floatKeys )
	
	eventDict = dict()
	
	for key in unifiedDict:
		eventName = unifiedDict[ key ][ 'event_name' ]
		if eventName not in eventDict:
			eventDict[ eventName ] = dict()
			eventDict[ eventName ][ 'event_id' ] = unifiedDict[ key ][ 'event_id' ]
			eventDict[ eventName ][ 'Gross' ] = unifiedDict[ key ][ 'Gross' ]
			eventDict[ eventName ][ 'Fee' ] = unifiedDict[ key ][ 'Fee' ]
			eventDict[ eventName ][ 'Net' ] = unifiedDict[ key ][ 'Net' ]
		else:
			eventDict[ eventName ][ 'Gross' ] = eventDict[ eventName ][ 'Gross' ] + unifiedDict[ key ][ 'Gross' ]
			eventDict[ eventName ][ 'Fee' ] = eventDict[ eventName ][ 'Fee' ] + unifiedDict[ key ][ 'Fee' ]
			eventDict[ eventName ][ 'Net' ] = eventDict[ eventName ][ 'Net' ] + unifiedDict[ key ][ 'Net' ]
			
	SaveTransactionDict(  report_filename, eventDict, [ 'event_name', 'event_id', 'Gross', 'Fee', 'Net' ] )
	
	
def GenerateCompleteReport( year_months ):
	event_report_transactionIDKey 	= 'event_name'
	event_report_StringKeys 		= [ 'event_id' ]
	unified_floatKeys	 			= [ 'Gross', 'Fee', 'Net' ]
	first_loop = True
	
	for ym in year_months:
		event_report_filename = 'event_report_' + ym + '.csv'		
		#print 'Processing ' + event_report_filename
		new_month = GenerateTransactionDict( event_report_filename, event_report_transactionIDKey, event_report_StringKeys, unified_floatKeys )
		if not first_loop:
			for key in new_month:
				if key in completeReport:
					#print 'Adding numbers for ' + key
					for floatField in unified_floatKeys:
						completeReport[ key ][ floatField ] = completeReport[ key ][ floatField ] + new_month[ key ][ floatField ]
				else:
					completeReport[ key ] = dict()
					#print 'Adding record for ' + key
					for field in new_month[ key ]:
						completeReport[ key ][ field ] = new_month[ key ][ field ]
		else:
			first_loop = False
			completeReport = dict()
			for key in new_month:
				#print 'Creating completeReport' + key
				completeReport[ key ] = dict()
				for field in new_month[ key ]:
					completeReport[ key ][ field ] = new_month[ key ][ field ]
					
	SaveTransactionDict(  'complete_report.csv', completeReport, [ 'event_name', 'event_id', 'Gross', 'Fee', 'Net' ] )


def GenerateYearMonths( startYear, startMonth, endYear, endMonth):
	list = []
    startMonth = max( min( startMonth, 12 ), 1 )
    endMonth = max( min( endMonth, 12 ), 1 )
    
	for year in range( startYear, endYear+1 ):
		if startYear == endYear:
			monthRange = range( startMonth, endMonth+1 )
		elif year == startYear:
			monthRange = range( startMonth, 13 )
		elif year == endYear:
			monthRange = range( 1, endMonth+1 )
		else:
			monthRange = range( 1, 13 )
			
		for month in monthRange:
			if month < 10:
				monthStr = "0" + str( month )
			else:
				monthStr = str( month )
			list.append( str( year ) + "_" + monthStr )
		
	return list
	
def ListCompare( l1, l2 ):
    if len( l1 ) is not len( l2 ):
        return False
    for i in range( len( l1 ) )
        if l1[ i ] is not l2[ i ]:
            return False
    return True
    
def GenerateWebsiteDict_UnitTest():
    year_months = GenerateYearMonths( 100, 1, 100, 12 )    
    if not ListCompare( year_month, [ '100_01', '100_02', '100_03', '100_04', '100_05', '100_06', '100_07', '100_08', '100_09', '100_10', '100_11', '100_12' ] ):
        print "GenerateWebsiteDict_UnitTest failed with ( 100, 1, 100, 12 )"
    
    year_months = GenerateYearMonths( 100, 0, 100, 5 )    
    if not ListCompare( year_month, [ '100_01', '100_02', '100_03', '100_04', '100_05' ] ):
        print "GenerateWebsiteDict_UnitTest failed with ( 100, 0, 100, 5 )"
    
    year_months = GenerateYearMonths( 100, 10, 100, 17 )    
    if not ListCompare( year_month, [ '100_10', '100_11', '100_12' ] ):
        print "GenerateWebsiteDict_UnitTest failed with ( 100, 10, 100, 17 )"
        
    year_months = GenerateYearMonths( 100, 10, 100, 1 )    
    if not ListCompare( year_month, [ ] ):
        print "GenerateWebsiteDict_UnitTest failed with ( 100, 10, 100, 1 )"

    year_months = GenerateYearMonths( 101, 1, 100, 10 )    
    if not ListCompare( year_month, [ ] ):
        print "GenerateWebsiteDict_UnitTest failed with ( 101, 1, 100, 10 )"
        
    year_months = GenerateYearMonths( 100, 10, 101, 1 )    

    if not ListCompare( year_month, [ '100_10', '100_11', '100_12', '101_01' ] ):
        print "GenerateWebsiteDict_UnitTest failed with ( 100, 10, 101, 1 )" 





        
def UniqueKeys( dict1, dict2 ):
    for key in dict1.keys():
        if key in dict2.keys():
            return False
    return True
    
    
class Record():
    transactionIDKey = ''
    stringKeys = []
    floatKeys = []
    records = dict()
    root_filename = ''
    
    def __init__( self, root_filename, transactionIDKey, stringKeys, floatKeys):
        self.root_filename = root_filename
        self.transactionIDKey = transactionIDKey
        self.stringKeys = stringKeys
        self.floatKeys = floatKeys
        
    def addToRecord( self, year_month ):
        filename = self.root_filename + '_' + year_month + '.csv'
        recordDict = GenerateTransactionDict( filename, self.transactionIDKey, self.stringKeys, self.floatKeys )
        
        if not UniqueKeys( recordDict, self.records ):
            print "Warning: " + filename + " has duplicate keys that will be overwritten."
            
        self.records.update( recordDict )

        
def GenerateWebsiteDict( year_months ):
    websiteRecords = dict()
    websiteRecords[ WebsiteKeys.refund ]            = Record( 'Refunds', 'refund_transaction_id', [ 'event_id', 'name' ], [] )
    websiteRecords[ WebsiteKeys.refund_original ]   = Record( 'Refunds', 'original_transaction_id', [ 'event_id', 'name', ], [] )
    websiteRecords[ WebsiteKeys.sales ]             = Record( 'Sales', 'transaction_id', [ 'event_id', 'name' ], [] )
    websiteRecords[ WebsiteKeys.fundraisers ]       = Record( 'Fundraisers', 'transaction_id', [ 'ticket_type' ], [] )
    websiteRecords[ WebsiteKeys.donations ]         = Record( 'Donations', 'transaction_id', [ 'event_id', 'name', 'identifier' ], [] )

    # TODO: generate based on monthly files and merge

    for ym in year_months:   
        websiteRecords[ WebsiteKeys.refund ].addToRecord( ym )
        websiteRecords[ WebsiteKeys.refund_original ].addToRecord( ym )
        websiteRecords[ WebsiteKeys.sales ].addToRecord( ym )
        websiteRecords[ WebsiteKeys.fundraisers ].addToRecord( ym )
        websiteRecords[ WebsiteKeys.donations ].addToRecord( ym )
        
    return websiteRecords
    
    



	
# Start of Script

year_months = GenerateYearMonths( 2012, 10, 2014, 12 )

for ym in year_months:
	paypal_filename = 'paypal_' + ym + '.csv'
	unified_filename = 'unified_' + ym + '.csv'
	event_report_filename = 'event_report_' + ym + '.csv'
	
	GenerateUnifiedRecord( paypal_filename, unified_filename )
	GenerateMonthlyReport( unified_filename, event_report_filename )
	

GenerateCompleteReport( year_months )
	
	
#GenerateUnifiedRecord( 'paypal_2012_12.csv', 'unified_2012_12.csv' )
#GenerateMonthlyReport( 'unified_2012_12.csv', 'event_report_2012_12.csv' )

	
	
