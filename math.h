#include <stdio.h>

int power(int val, int exp) 	{
	int prod = 1;
	for(int i = 0; i < exp; i+=1) 	prod *= val;

	return prod;
}
