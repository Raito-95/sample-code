# Grade System

This Python program allows you to manage and manipulate student grade data. It provides functionality for importing, querying, adding, deleting, and sorting student grades.

## Features

- Query a student's single subject grade.
- Retrieve all grades for a student.
- Add new student grade data.
- Delete student grade data.
- Sort student grades using Radix Sort.

## Usage

1. Run the `GradeSystem.py` script.

2. Follow the on-screen menu to select the desired functionality.

3. Follow the prompts to perform specific operations, such as querying grades or adding new data.

4. Use the sorting functionality to sort student grades by subject using Radix Sort.

## File Formats

- You can import student grade data from a text file with the following format:

```
97501 DS 80 DM 76 LA 63
97502 DS 53 DM 79 LA 98
97523 DS 83 DM 49 LA 78
```

- The format is as follows:

  - Student ID
  - Subject 1 Name
  - Subject 1 Score
  - Subject 2 Name
  - Subject 2 Score
  - Subject 3 Name
  - Subject 3 Score

- DS: Data Structure, DM: Discrete Mathematics, LA: Linear Algebra

## Example Usage

### Scenario 1:

1. Select "5" to sort grades.
2. Enter the subject name (e.g., DS).
3. Choose Radix Sort to sort the grades.

### Scenario 2:

1. Create a text file (e.g., grade1.txt) with the specified format.
2. Run the program and follow the menu options to read and manipulate data.

### Scenario 3:

1. Follow the on-screen menu to select functionality.
2. Choose "5" to sort grades.
3. Enter the subject name (e.g., DS).
4. Choose a sorting method, e.g., Radix Sort.
5. View the sorted grades.

### Scenario 4:

1. Create a text file (e.g., grade2.txt) with the specified format.
2. Run the program and follow the menu options to read and manipulate data.

   #### Sub-Scenario 1:

   - Select "3" to add new student grade data.
   - Enter the student ID and grade data.
   - Confirm that the data was added successfully.

   #### Sub-Scenario 2:

   - Select "2" to query all grades for a student.
   - Enter the student ID.
   - View the student's grades.

   #### Sub-Scenario 3:

   - Select "4" to delete student grade data.
   - Enter the student ID to delete.
   - Confirm that the data was deleted successfully.

   #### Sub-Scenario 4:

   - Select "2" to query all grades for a student.
   - Enter the student ID.
   - Confirm that the student has no data.