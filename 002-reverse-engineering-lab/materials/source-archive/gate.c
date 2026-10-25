#include <stdio.h>
#include <string.h>

static int confere(const char *entrada)
{
    const unsigned char *s = (const unsigned char *)entrada;
    if (strlen(entrada) != 6) return 0;

    return s[0] + 3 == 70 &&
           (s[1] ^ 0x55) == 0x65 &&
           s[2] - s[0] == 15 &&
           s[3] + s[1] == 117 &&
           (s[4] ^ s[2]) == 0x66 &&
           s[5] + s[4] == 102;
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "uso: %s CHAVE\n", argv[0]);
        return 2;
    }
    if (!confere(argv[1])) {
        puts("porta fechada");
        return 1;
    }
    puts("porta aberta");
    return 0;
}
