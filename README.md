# BELComparator

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=fff&labelColor=grey&color=yellowgreen)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/WoongyuChoi/BELComparator/blob/main/LICENSE)
![Platform](https://img.shields.io/badge/platform-desktop-blue)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/WoongyuChoi/BELComparator)

<figure align="center">
    <img src="https://github.com/user-attachments/assets/da6056d1-57b0-4f63-946c-b9be439e313b" width="80%"/>
</figure>

## Overview
**BELComparator** is a Python-based tool designed to compare values between two CSV files, referred to as the First CSV and the Second CSV. Built with a user-friendly GUI in PyQt5, this application allows for easy file loading, value entry, and customizable comparison.

## Features

- **Load CSV Files**: Import First and Second CSV files for comparison.
- **Input Values**: Manually input values to use in comparisons.
- **Data Range Selection**: Define a specific range within the First CSV file for targeted comparison.
- **Tolerance Setting**: Filter differences by setting an acceptable tolerance level.
- **View Modes**: Choose between viewing all data or filtering only items outside the tolerance.
- **Exclude N/A Values**: Option to exclude rows with `N/A` in the comparison results.
- **Comparison Results**: View side-by-side differences between the First and Second CSV values in a table.
- **Index Mapping**: Identify and map row indexes between the two datasets.
- **Error Handling**: Robust error handling for missing columns, row mismatches, and more.
- **Export Results**: Save the comparison results as a new CSV file.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/WoongyuChoi/BELComparator.git
   cd BELComparator
   ```

2. Install Dependencies:
   Make sure you have Python 3.7+ installed. Then, install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Application:
   ```bash
   python main.py
   ```

## Usage

1. **Load CSV Files**: Use the GUI to load the First and Second CSV files.
2. **Enter Values**: Enter desired values for comparison in the input field.
3. **Set Data Range and Tolerance**: Optionally specify a data range and tolerance level.
4. **Choose Comparison Options**: Toggle options such as full view, filtered view (differences only), and exclude N/A values.
5. **Perform Comparison**: Click "Compare" to run the comparison.
6. **View Results**: Results are displayed in a table showing differences.
7. **Export Results**: Export the table as a CSV file if needed.

## License

This project is licensed under the MIT License.
