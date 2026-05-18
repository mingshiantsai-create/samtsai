import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# Create workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "TW PAC Benchmarking"

# Define colors
green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
light_green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

# Headers
headers = ["", "A", "B", "C", "D", "E", "F", "G", "H"]
criteria = [
    "TW PAC-High-end",
    "Full-line (Capacity range)",
    "Full-line (Indoor Type)",
    "Full-line (Control Solution)",
    "Performance (Efficiency)",
    "Performance (Noise/ESP/etc.)",
    "Footprint (Dimension)",
    "Feature",
    "Industry design",
    "Price",
    "PAC"
]

weights = [
    "",
    "20%",
    "15%",
    "10%",
    "15%",
    "10%",
    "10%",
    "15%",
    "5%",
    "30%",
    "100%"
]

brands = ["Hitachi", "Daikin", "MHI", "Mistubishi Electric", "Panasonic"]

# Set column widths
ws.column_dimensions['A'].width = 30
for col in ['B', 'C', 'D', 'E', 'F', 'G', 'H']:
    ws.column_dimensions[col].width = 18

# Row 1: Headers with brands
ws['A1'] = "TW PAC-High-end"
ws['A1'].fill = green_fill
ws['A1'].font = Font(bold=True)

for idx, brand in enumerate(brands, start=3):
    col_letter = openpyxl.utils.get_column_letter(idx)
    ws[f'{col_letter}1'] = brand
    ws[f'{col_letter}1'].fill = green_fill
    ws[f'{col_letter}1'].font = Font(bold=True)

# Add criteria and weights
for row_idx, (criterion, weight) in enumerate(zip(criteria[1:], weights[1:]), start=2):
    ws[f'A{row_idx}'] = criterion
    ws[f'B{row_idx}'] = weight
    
    # Apply fill to header row
    if row_idx == 2:
        ws[f'A{row_idx}'].fill = light_green_fill

# Rating-PAC section
ws['A13'] = "Rating-PAC"
ws['B13'] = "%"
ws['C13'] = "1(Worst)"
ws['D13'] = "2"
ws['E13'] = "3"
ws['F13'] = "4"
ws['G13'] = "5"

# VRF section
ws['A15'] = "VRF 側吹"

# Save file
wb.save("TW_PAC_Benchmarking0518.xlsx")
print("✓ Excel檔案已建立: TW_PAC_Benchmarking0518.xlsx")
