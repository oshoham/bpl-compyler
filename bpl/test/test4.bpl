int y;

int f(int x) {
    y = 5;
    return x;
}

void main(void) {
    f(34);
    write(y);
}
