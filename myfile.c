#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <stdbool.h>

int add_int(int a, int b) {
    return a +  b;
}

double add_double(double a, double b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

bool isEven(int num) {
    return num %  2 == 0;
}

bool isPrime(int n) {
    if (n <= 1) return false;
    for (int i = 2; i * i <= n; ++i)
        if (n % i == 0) return  false;
    return true;
}

int* generatePrimes(int count, int* outputSize) {
    int* primes = (int*)malloc(sizeof(int) * count);
    int found = 0;
    for (int i = 2; found < count; ++i) {
        if (isPrime(i)) {
            primes[found++] = i;
        }
    }
    *outputSize = found;
    return primes;
}

void printArray(int* arr, int size) {
    for (int i = 0; i < size; ++i)
        printf("%d ", arr[i]);
    printf("\n");
}

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

void printFactorials(int upto) {
    for (int i = 1; i <= upto; ++i)
        printf("Factorial of %d: %d\n", i, factorial(i));
}

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

void printFibonacci(int count) {
    for (int i = 0; i < count; ++i)
        printf("%d ", fibonacci(i));
    printf("\n");
}

int maxInArray(int* arr, int size) {
    int max = arr[0];
    for (int i = 1; i < size; ++i)
        if (arr[i] > max) max = arr[i];
    return max;
}

int minInArray(int* arr, int size) {
    int min = arr[0];
    for (int i = 1; i < size; ++i)
        if (arr[i] < min) min = arr[i];
    return min;
}

double average(int* arr, int size) {
    int sum = 0;
    for (int i = 0; i < size; ++i)
        sum += arr[i];
    return (double)sum / size;
}

bool contains(int* arr, int size, int val) {
    for (int i = 0; i < size; ++i)
        if (arr[i] == val) return true;
    return false;
}

void reverseArray(int* arr, int size) {
    for (int i = 0; i < size / 2; ++i) {
        int t = arr[i];
        arr[i] = arr[size - i - 1];
        arr[size - i - 1] = t;
    }
}

void sortArray(int* arr, int size) {
    for (int i = 0; i < size - 1; ++i)
        for (int j = i + 1; j < size; ++j)
            if (arr[i] > arr[j]) {
                int t = arr[i];
                arr[i] = arr[j];
                arr[j] = t;
            }
}

int gcd(int a, int b) {
    return b == 0 ? a : gcd(b, a % b);
}

int lcm(int a, int b) {
    return (a * b) / gcd(a, b);
}

void toUpperStr(char* str) {
    for (int i = 0; str[i]; ++i)
        str[i] = toupper(str[i]);
}

void toLowerStr(char* str) {
    for (int i = 0; str[i]; ++i)
        str[i] = tolower(str[i]);
}

bool isPalindrome(const char* str) {
    int len = strlen(str);
    for (int i = 0; i < len / 2; ++i)
        if (str[i] != str[len - 1 - i]) return false;
    return true;
}

int countVowels(const char* str) {
    int count = 0;
    for (int i = 0; str[i]; ++i)
        if (strchr("aeiouAEIOU", str[i])) count++;
    return count;
}

void printAsciiTable() {
    for (int i = 32; i < 128; ++i)
        printf("%d: %c\n", i, i);
}

void swapValues(int* a, int* b) {
    int t = *a;
    *a = *b;
    *b = t;
}

int sumOfDigits(int num) {
    int sum = 0;
    while (num > 0) {
        sum += num % 10;
        num /= 10;
    }
    return sum;
}

int power(int base, int exp) {
    int result = 1;
    for (int i = 0; i < exp; ++i)
        result *= base;
    return result;
}

void drawBox(int size) {
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j)
            printf("* ");
        printf("\n");
    }
}

void printMultiplicationTable(int n) {
    for (int i = 1; i <= 10; ++i)
        printf("%d x %d = %d\n", n, i, n * i);
}

bool isLeapYear(int year) {
    return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0);
}

void countDown(int n) {
    while (n >= 0) {
        printf("%d ", n--);
    }
    printf("\n");
}

void fizzBuzz(int n) {
    for (int i = 1; i <= n; ++i) {
        if (i % 15 == 0) printf("FizzBuzz ");
        else if (i % 3 == 0) printf("Fizz ");
        else if (i % 5 == 0) printf("Buzz ");
        else printf("%d ", i);
    }
    printf("\n");
}

bool isArmstrong(int num) {
    int sum = 0, temp = num, n = 0;
    while (temp) { temp /= 10; ++n; }
    temp = num;
    while (temp) {
        int digit = temp % 10;
        sum += power(digit, n);
        temp /= 10;
    }
    return sum == num;
}

void printBarChart(int* arr, int size) {
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < arr[i]; ++j)
            printf("*");
        printf("\n");
    }
}

int sumRange(int start, int end) {
    int sum = 0;
    for (int i = start; i <= end; ++i)
        sum += i;
    return sum;
}

bool areAnagrams(const char* a, const char* b) {
    int ca[256] = {0}, cb[256] = {0};
    for (int i = 0; a[i]; ++i) ca[(unsigned char)a[i]]++;
    for (int i = 0; b[i]; ++i) cb[(unsigned char)b[i]]++;
    for (int i = 0; i < 256; ++i)
        if (ca[i] != cb[i]) return false;
    return true;
}

void drawTriangle(int height) {
    for (int i = 1; i <= height; ++i) {
        for (int j = 0; j < i; ++j)
            printf("*");
        printf("\n");
    }
}

void drawPyramid(int height) {
    for (int i = 1; i <= height; ++i) {
        for (int j = 0; j < height - i; ++j) printf(" ");
        for (int j = 0; j < 2 * i - 1; ++j) printf("*");
        printf("\n");
    }
}

void greeting(const char* name) {
    printf("Hello, %s!\n", name);
}

int sumOfSquares(int n) {
    int sum = 0;
    for (int i = 1; i <= n; ++i) sum += i * i;
    return sum;
}

bool isPerfectSquare(int x) {
    int s = sqrt(x);
    return s * s == x;
}

void printTable(int rows, int cols) {
    for (int i = 1; i <= rows; ++i) {
        for (int j = 1; j <= cols; ++j)
            printf("%d\t", i * j);
        printf("\n");
    }
}

int charCount(const char* str, char ch) {
    int count = 0;
    for (int i = 0; str[i]; ++i)
        if (str[i] == ch) count++;
    return count;
}

void welcomeBanner() {
    printf("====================\n");
    printf("   Welcome User!\n");
    printf("====================\n");
}

int main() {
    welcomeBanner();
    greeting("Prashant");
    
    int primeCount = 10;
    int actualSize = 0;
    int* primes = generatePrimes(primeCount, &actualSize);
    printArray(primes, actualSize);
    free(primes);

    printFibonacci(10);
    printFactorials(5);

    printf("Sum of digits (1234): %d\n", sumOfDigits(1234));
    printf("LCM of 12 and 18: %d\n", lcm(12, 18));
    printf("Is 'madam' palindrome? %s\n", isPalindrome("madam") ? "Yes" : "No");
    drawPyramid(5);

    return 0;
}
