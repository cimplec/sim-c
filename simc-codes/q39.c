#include <stdio.h>
{
	int p;
	printf("Input principle : ");
	scanf("%d", &p);
	int r;
	printf("Input Rate of interest : ");
	scanf("%d", &r);
	int t;
	printf("Input Time : ");
	scanf("%d", &t);
	int amount = p * r * t / 100;
	printf("Simple interest =");
	printf("%d", amount);
}
