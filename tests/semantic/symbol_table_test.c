#include "semantic/symbol_table.h"

#include <stdio.h>

int main(void)
{
    SymbolTable *table;
    const Symbol *symbol;

    table = symbol_table_create(16);

    if (table == NULL)
    {
        printf("Failed to create symbol table.\n");
        return 1;
    }

    if (!symbol_table_insert(table, "aws", SYMBOL_CLOUD))
    {
        printf("Failed to insert aws.\n");
        symbol_table_destroy(table);
        return 1;
    }

    if (!symbol_table_insert(table, "web", SYMBOL_SERVER))
    {
        printf("Failed to insert web.\n");
        symbol_table_destroy(table);
        return 1;
    }

    if (symbol_table_insert(table, "aws", SYMBOL_CLOUD))
    {
        printf("Duplicate insertion was incorrectly accepted.\n");
        symbol_table_destroy(table);
        return 1;
    }

    symbol = symbol_table_lookup(table, "aws");

    if (symbol == NULL)
    {
        printf("aws was not found.\n");
        symbol_table_destroy(table);
        return 1;
    }

    printf(
        "%s: %s\n",
        symbol->name,
        symbol_kind_name(symbol->kind)
    );

    printf("Contains web: %s\n",
           symbol_table_contains(table, "web") ? "yes" : "no");

    printf("Contains missing: %s\n",
           symbol_table_contains(table, "missing") ? "yes" : "no");

    printf("Symbol count: %zu\n", symbol_table_size(table));

    symbol_table_destroy(table);

    return 0;
}