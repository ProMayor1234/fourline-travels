     # Four-Line Travels Invoice Generator

     ## Web App

     From the project root, install the dependencies and start the Flask server:

     ```bash
     pip install -r requirements.txt
     python -m flask --app app run
     ```

     Open <http://127.0.0.1:5000> in a browser. Select a billing mode, upload a CSV or Excel file, and download the generated invoice when processing is complete.

     Generated invoices are saved in the `Output/` folder.

     ## Command-Line App

     To use the original interactive version instead:

     ```bash
     python Code/main
     ```

     Select a billing mode when prompted. The invoice is written to `Output/invoice.txt`.

     ## CSV Format

     Each upload must include `patient_name` and the billing field for its selected mode.

     ### UHC

     Required billing field: `miles`

     Other supported columns: `invoice_number`, `dob`, `member_id`, `service_type`, `date_of_service`, `facility_name`

     ### NJ Veterans

     Required billing field: `hours`

     Other supported columns: `date_of_service`, `facility_name`, `destination_address`, `service_type`

     ### Jewish Home

     Required billing field: `miles`

     Other supported columns: `item`, `date_of_service`, `confirmation_no`, `from_address`, `to_address`