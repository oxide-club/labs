#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Mensagem { char *texto; };

static void descarta(struct Mensagem *m)
{
    free(m->texto);
    m->texto = NULL;
}

int main(void)
{
    struct Mensagem m = { malloc(sizeof "Oxide Club") };
    if (!m.texto) return 2;
    memcpy(m.texto, "Oxide Club", sizeof "Oxide Club");

    const char *visao = m.texto + 6;

    descarta(&m);
    for (size_t i = 0; visao[i] != '\0'; ++i)
        putchar(visao[i]);
    putchar('\n');

    return 0;
}
