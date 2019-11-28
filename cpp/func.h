// http://katsura-kotonoha.sakura.ne.jp/prog/c/tip0000a.shtml
int gcm(int m, int n){
	// 引数に０がある場合は０を返す
	if( ( 0 == m ) || ( 0 == n ) ) return 0;
	
	// ユークリッドの方法
	while(m != n){
		if(m > n) m = m - n;
		else n = n - m;
	}
	return m;
}

int lcm(int m, int n){
	// 引数に０がある場合は０を返す
	if( ( 0 == m ) || ( 0 == n ) ) return 0;
	
	return ((m / gcm(m, n)) * n); // lcm = m * n / gcd(m,n)
}

int multi_lcm(int *num, int size){
	int tmp = num[0];
	for(int i = 1; i < size; i++){
		tmp = lcm(tmp, num[i]);
	}
	return tmp;
}