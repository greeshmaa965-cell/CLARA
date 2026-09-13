#include "semantic/symbol_table.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static char *duplicate_string(const char *text)
{
    char *copy;

    if (text == NULL)
    {
        return NULL;
    }

    copy = malloc(strlen(text) + 1);

    if (copy == NULL)
    {
        return NULL;
    }

    strcpy(copy, text);
    return copy;
}

static size_t hash_string(const char *text, size_t bucket_count)
{
    size_t hash = 5381;
    unsigned char character;

    if (bucket_count == 0)
    {
        return 0;
    }

    while (*text != '\0')
    {
        character = (unsigned char)*text;
        hash = ((hash << 5) + hash) ^ character;
        text++;
    }

    return hash % bucket_count;
}

SymbolTable *symbol_table_create(size_t bucket_count)
{
    SymbolTable *table;

    if (bucket_count == 0)
    {
        bucket_count = 16;
    }

    table = calloc(1, sizeof(SymbolTable));

    if (table == NULL)
    {
        return NULL;
    }

    table->buckets = calloc(bucket_count, sizeof(Symbol *));

    if (table->buckets == NULL)
    {
        free(table);
        return NULL;
    }

    table->bucket_count = bucket_count;
    table->symbol_count = 0;

    return table;
}

void symbol_table_destroy(SymbolTable *table)
{
    size_t i;
    Symbol *current;
    Symbol *next;

    if (table == NULL)
    {
        return;
    }

    for (i = 0; i < table->bucket_count; i++)
    {
        current = table->buckets[i];

        while (current != NULL)
        {
            next = current->next;

            free(current->name);
            free(current);

            current = next;
        }
    }

    free(table->buckets);
    free(table);
}

int symbol_table_insert(
    SymbolTable *table,
    const char *name,
    SymbolKind kind
)
{
    size_t index;
    Symbol *current;
    Symbol *symbol;

    if (table == NULL || name == NULL || name[0] == '\0')
    {
        return 0;
    }

    index = hash_string(name, table->bucket_count);

    current = table->buckets[index];

    while (current != NULL)
    {
        if (strcmp(current->name, name) == 0)
        {
            return 0;
        }

        current = current->next;
    }

    symbol = calloc(1, sizeof(Symbol));

    if (symbol == NULL)
    {
        return 0;
    }

    symbol->name = duplicate_string(name);

    if (symbol->name == NULL)
    {
        free(symbol);
        return 0;
    }

    symbol->kind = kind;
    symbol->next = table->buckets[index];
    table->buckets[index] = symbol;
    table->symbol_count++;

    return 1;
}

const Symbol *symbol_table_lookup(
    const SymbolTable *table,
    const char *name
)
{
    size_t index;
    const Symbol *current;

    if (table == NULL || name == NULL || name[0] == '\0')
    {
        return NULL;
    }

    index = hash_string(name, table->bucket_count);
    current = table->buckets[index];

    while (current != NULL)
    {
        if (strcmp(current->name, name) == 0)
        {
            return current;
        }

        current = current->next;
    }

    return NULL;
}

int symbol_table_contains(
    const SymbolTable *table,
    const char *name
)
{
    return symbol_table_lookup(table, name) != NULL;
}

const char *symbol_kind_name(SymbolKind kind)
{
    switch (kind)
    {
        case SYMBOL_CLOUD:
            return "CLOUD";

        case SYMBOL_SERVER:
            return "SERVER";

        case SYMBOL_DATABASE:
            return "DATABASE";

        default:
            return "UNKNOWN";
    }
}

size_t symbol_table_size(const SymbolTable *table)
{
    if (table == NULL)
    {
        return 0;
    }

    return table->symbol_count;
}