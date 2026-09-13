#ifndef CLARA_SYMBOL_TABLE_H
#define CLARA_SYMBOL_TABLE_H

#include <stddef.h>

typedef enum
{
    SYMBOL_CLOUD,
    SYMBOL_SERVER,
    SYMBOL_DATABASE
} SymbolKind;

typedef struct Symbol
{
    char *name;
    SymbolKind kind;

    struct Symbol *next;
} Symbol;

typedef struct SymbolTable
{
    Symbol **buckets;
    size_t bucket_count;
    size_t symbol_count;
} SymbolTable;

SymbolTable *symbol_table_create(size_t bucket_count);

void symbol_table_destroy(SymbolTable *table);

int symbol_table_insert(
    SymbolTable *table,
    const char *name,
    SymbolKind kind
);

const Symbol *symbol_table_lookup(
    const SymbolTable *table,
    const char *name
);

int symbol_table_contains(
    const SymbolTable *table,
    const char *name
);

const char *symbol_kind_name(SymbolKind kind);

size_t symbol_table_size(const SymbolTable *table);

#endif