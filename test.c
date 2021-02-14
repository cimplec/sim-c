#include <stdio.h>

int sum(int a, int b) 	{

	return a + b;
}

int main() {
	int a = 1;
	int b = 2;
	int c = sum(a, b);
	{
	float a = 3.14;
	float b = 5.6;
	float c = a + b;
	{
	char* c = "hello";
	printf("%s", c);
	}
	printf("%f", c);
	}
	printf("%d", c);

	return 0;
}
