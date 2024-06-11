# Time Complexity and Space Complexity

## Time Complexity

Time complexity is a computational complexity that describes the amount of time it takes to run an algorithm. The time complexity of an algorithm is commonly expressed using Big O notation, which categorizes algorithms based on how their run time or space requirements grow as the input size grows.

### Common Time Complexities

- **O(1)**: Constant time - the algorithm's run time does not change regardless of the input size.
- **O(log n)**: Logarithmic time - the run time grows logarithmically with the input size.
- **O(n)**: Linear time - the run time grows linearly with the input size.
- **O(n log n)**: Linearithmic time - the run time grows linearly and logarithmically with the input size.
- **O(n^2)**: Quadratic time - the run time grows quadratically with the input size.
- **O(2^n)**: Exponential time - the run time grows exponentially with the input size.

### Examples

- **O(1)**: Accessing an element in an array by index.
- **O(log n)**: Binary search in a sorted array.
- **O(n)**: Linear search in an array.
- **O(n log n)**: Merge sort and quicksort in their average cases.
- **O(n^2)**: Bubble sort, selection sort, and insertion sort in their worst cases.
- **O(2^n)**: Solving the Tower of Hanoi problem.

## Space Complexity

Space complexity refers to the amount of memory space required by an algorithm to run as a function of the input size. Similar to time complexity, space complexity is also expressed using Big O notation.

### Common Space Complexities

- **O(1)**: Constant space - the algorithm's space requirement does not change regardless of the input size.
- **O(n)**: Linear space - the space requirement grows linearly with the input size.
- **O(n^2)**: Quadratic space - the space requirement grows quadratically with the input size.

### Examples

- **O(1)**: A simple loop that requires a fixed amount of extra space.
- **O(n)**: Storing a list of elements.
- **O(n^2)**: Creating a 2D array of size n by n.

## Conclusion

Understanding the time and space complexity of algorithms is crucial for writing efficient code. It helps in predicting the performance and resource utilization of algorithms, which is essential for developing scalable and high-performance applications.
