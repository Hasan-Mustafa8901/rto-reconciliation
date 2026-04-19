# RTO Reconciliation Software – User Documentation

## 1. Purpose of the Software

The **RTO Reconciliation Tool** is used to match and reconcile vehicle delivery data with RTO registration data.
It compares both datasets and generates a final reconciliation output Excel file.

This document explains:

* Required Excel file structure
* How to use the software step-by-step
* Common errors and fixes

---

# 2. Required Excel File Structure (IMPORTANT)

The application only works if the Excel file contains **two specific sheets** with correct column names.

## Sheet 1: Delivery Data

### Required Sheet Name

`Delivery Data`

### Required Columns (exact spelling recommended)

* Delivery Date
* Customer Name
* Chassis Number
* VIN Number
* Showroom

### Notes

* Column order does NOT matter.
* Extra columns are allowed.
* Column names should not contain extra spaces.
* Avoid spelling mistakes.

---

## Sheet 2: RTO Data

### Required Sheet Name

`RTO Data`

### Required Columns

* Office Name
* Dealer Name
* Vehicle Registration Number
* Owner Name
* Chassis Number
* VIN Number

### Notes

* Column names must be present.
* Extra columns are allowed (ignored automatically).
* Avoid blank header rows above actual headers.

---

# 3. Important Formatting Rules

To avoid errors:

### Do NOT:

* Add spaces before/after column names
  Example: `" Chassis Number "` ❌
* Change column spelling
  Example: `"Chassis No"` ❌
* Change sheet names
  Example: `"Delivery"` ❌

### Allowed:

* Extra columns (ignored automatically)
* Any number of rows
* Any column order

The software will automatically warn if:

* Columns are missing
* Case mismatch exists
* Extra spaces exist
* Extra columns exist

---

# 4. How to Use the Software

Follow these steps carefully.

## Step 1: Load Excel File

1. Open the application.
2. Click **Load File**.
3. Select the Excel file containing:

   * Delivery Data sheet
   * RTO Data sheet

After loading:

* File name will appear in green.
* Sheet dropdown will be populated.
* Header check will run automatically.

If there are issues → they will appear in the **Messages box**.

---

## Step 2: Verify Sheet Information

After loading:

* Select each sheet from dropdown.
* Check:

  * Number of rows
  * Number of columns
  * Headers preview
  * Warning messages (if any)

Fix issues in Excel if warnings appear.

---

## Step 3: Select Dealership

Choose one dealership:

* BR Hyundai
* SAS Hyundai
* JSV Hyundai

Reconciliation will run according to selected dealership.

---

## Step 4: Choose Output Location

Click:
**Choose Output Location**

Select the folder where final output file will be saved.

---

## Step 5: Run Reconciliation

Click:
**Get RTO Reco**

The system will:

1. Validate file structure
2. Run reconciliation pipeline
3. Generate output Excel

Messages will display progress.

---

# 5. Output File

After successful run:

A final Excel file will be generated in the selected folder.

The message box will show:
Output file path

Example:
Output file generated:
C:\Users...\RTO_Reco_Output.xlsx

---



# 6. Error Handling

## "Please load an Excel file first"

You clicked Run without loading file.

## "Please select a dealership"

Select dealership before running.

## Missing columns warning

Fix Excel column names exactly as required.

## Headers with spaces warning

Remove extra spaces from column names.

## Case mismatch warning

Match exact column casing.

---

# 7. Best Practices

* Always use template Excel format.
* Do not rename sheets.
* Do not merge header cells.
* Keep headers in first row.
* Save file before loading.

---

# 8. Recommended Workflow (Fastest)

1. Prepare Excel file (correct format)
2. Open software
3. Load file
4. Select dealership
5. Choose output folder
6. Click **Get RTO Reco**
7. Collect output

Total time: < 1 minute once file is ready.

---

# 9. Support

If reconciliation fails:

1. Read messages box carefully
2. Fix Excel structure
3. Run again

If still failing → contact developer with input file.

10. 
