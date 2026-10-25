/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Message { char *text; };

static void discard(struct Message *message) {
    free(message->text);
    message->text = NULL;
}

int main(int argc, char **argv) {
    if (argc != 2 || (strcmp(argv[1], "borrowed") && strcmp(argv[1], "owner-null")
            && strcmp(argv[1], "copy") && strcmp(argv[1], "reset"))) {
        fputs("uso: lifetimes borrowed|owner-null|copy|reset\n", stderr);
        return 2;
    }
    struct Message owner = {malloc(sizeof "Oxide Club")};
    if (!owner.text) return 2;
    memcpy(owner.text, "Oxide Club", sizeof "Oxide Club");
    const char *view = owner.text + 6;
    if (!strcmp(argv[1], "borrowed")) {
        puts(view); /* Bloco ainda vivo. */
        discard(&owner);
    } else if (!strcmp(argv[1], "owner-null")) {
        discard(&owner);
        printf("owner_null=%d\n", owner.text == NULL);
        fflush(stdout);
        puts(view); /* Defeito intencional: execução isolada sob ASan. */
    } else if (!strcmp(argv[1], "copy")) {
        char *copy = malloc(sizeof "Club");
        if (!copy) { discard(&owner); return 2; }
        memcpy(copy, view, sizeof "Club");
        discard(&owner);
        puts(copy);
        free(copy);
    } else {
        /* Modelo mínimo de invalidação lógica. Não há free no reset. */
        unsigned generation = 1;
        const unsigned old_generation = generation;
        ++generation;
        memcpy(owner.text, "Oxide Rust", sizeof "Oxide Rust");
        printf("old_generation=%u current_generation=%u\n", old_generation, generation);
        printf("old_handle_valid=%d addressable=%s\n", old_generation == generation, view);
        /* A leitura acima é válida em C; viola a validade lógica do handle antigo.
           É uma observação controlada, não uma implementação segura de arena. */
        discard(&owner);
    }
    return 0;
}
