#include <stdio.h>
#include "math.h"
#include "geometry.h"

int main() {
	int num = 3;
	int num_sq = power(3, 2);
	int result = square_area(num_sq);
	printf("%d", result);

	return 0;
}
