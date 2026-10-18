#ifndef CLARA_IR_H
#define CLARA_IR_H

#include <stddef.h>
#include "ast/ast.h"

typedef struct
{
    char name[64];
    int cpu;
    double memory_gb;
    double storage_gb;
} IRServer;

typedef struct
{
    char name[64];
    int cpu;
    double memory_gb;
    double storage_gb;
} IRDatabase;

typedef struct
{
    char provider[32];
    char region[64];

    IRServer *servers;
    size_t server_count;
    size_t server_capacity;

    IRDatabase *databases;
    size_t database_count;
    size_t database_capacity;
} CLARA_IR;

/* Converts a validated AST into intermediate representation with normalized units (GB) */
CLARA_IR *ir_build_from_ast(const ASTNode *ast);

/* Frees memory associated with intermediate representation */
void ir_destroy(CLARA_IR *ir);

/* Serializes the IR into canonical formatted JSON */
char *ir_to_json(const CLARA_IR *ir);

/* Prints human-readable summary of IR */
void ir_print(const CLARA_IR *ir);

#endif
